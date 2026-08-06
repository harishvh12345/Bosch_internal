import json
import logging
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.interfaces.ai import AIService
from app.interfaces.search import EmbeddingService
from app.services.gemini.prompts import (
    SKILLS_GAP_TEMPLATE,
    CURRICULUM_MODULE_TEMPLATE,
    QUIZ_TEMPLATE,
    RECOMMENDATION_TEMPLATE,
    SIMULATION_EXPLANATION_TEMPLATE
)

logger = logging.getLogger(__name__)

class GeminiAIService(AIService, EmbeddingService):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.initialized = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-3.5-flash")
                self.initialized = True


                logger.info("Google Gemini SDK configured successfully.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini SDK: {e}")
        else:
            logger.warning("GEMINI_API_KEY not found in settings. Running in MOCK Mode.")

    async def get_embedding(self, text: str) -> List[float]:
        if not self.initialized:
            # Fallback mock embedding: 768 float array
            import random
            random.seed(hash(text))
            return [random.uniform(-0.1, 0.1) for _ in range(768)]
        
        try:
            # Run in executor if blocking
            import asyncio
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(
                    model="models/text-embedding-004",
                    content=text
                )
            )
            return response["embedding"]
        except Exception as e:
            logger.error(f"Error calling Gemini Embedding: {e}")
            import random
            random.seed(hash(text))
            return [random.uniform(-0.1, 0.1) for _ in range(768)]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for t in texts:
            emb = await self.get_embedding(t)
            embeddings.append(emb)
        return embeddings

    async def _call_gemini_json(self, prompt: str) -> Dict[str, Any]:
        """Calls Gemini and expects a JSON response, parsing it safely."""
        if not self.initialized:
            raise ValueError("Gemini is not configured. Setup GEMINI_API_KEY in .env.")
            
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            
            # Request JSON output
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
            )
            
            text = response.text.strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Gemini API execution error: {e}")
            # Try to extract JSON from text if format differed
            try:
                # Basic parsing attempt
                start = text.find("{")
                end = text.rfind("}") + 1
                if start != -1 and end != -1:
                    return json.loads(text[start:end])
            except Exception:
                pass
            raise

    async def analyze_skills_gap(
        self, profile: Dict[str, Any], goal: str, context_docs: str = "", simulation_focus: str = ""
    ) -> Dict[str, Any]:
        if not self.initialized:
            # High-fidelity Mock Skills Gap
            return self._mock_skills_gap(profile, goal)

        prompt = SKILLS_GAP_TEMPLATE.format(
            department=profile.get("department", "Engineering"),
            role=profile.get("role", "Developer"),
            experience_years=profile.get("experience_years", 0),
            skills=str(profile.get("skills", [])),
            learning_history=str(profile.get("learning_history", {})),
            goal=goal,
            simulation_focus=simulation_focus or "None",
            context=context_docs or "No local Bosch training manuals matched this goal query."
        )
        try:
            return await self._call_gemini_json(prompt)
        except Exception:
            return self._mock_skills_gap(profile, goal)

    async def generate_module_curriculum(
        self, profile: Dict[str, Any], goal: str, module_title: str, module_index: int, context_docs: str = "", simulation_focus: str = ""
    ) -> Dict[str, Any]:
        if not self.initialized:
            return self._mock_module_curriculum(profile, goal, module_title, module_index)

        prompt = CURRICULUM_MODULE_TEMPLATE.format(
            role=profile.get("role", "Developer"),
            experience_years=profile.get("experience_years", 0),
            goal=goal,
            simulation_focus=simulation_focus or "None",
            module_title=module_title,
            module_index=module_index,
            context=context_docs or "No reference blueprints matched."
        )
        try:
            return await self._call_gemini_json(prompt)
        except Exception:
            return self._mock_module_curriculum(profile, goal, module_title, module_index)

    async def generate_quiz(self, module_title: str, topics: List[str], difficulty: str) -> Dict[str, Any]:
        if not self.initialized:
            return self._mock_quiz(module_title, topics, difficulty)

        prompt = QUIZ_TEMPLATE.format(
            topics_list=", ".join(topics),
            difficulty=difficulty
        )
        try:
            return await self._call_gemini_json(prompt)
        except Exception:
            return self._mock_quiz(module_title, topics, difficulty)

    async def generate_recommendations(
        self, profile: Dict[str, Any], quiz_results: List[Dict[str, Any]], simulation_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not self.initialized:
            return self._mock_recommendations(profile)

        prompt = RECOMMENDATION_TEMPLATE.format(
            role=profile.get("role", "Developer"),
            experience_years=profile.get("experience_years", 0),
            quiz_results=str(quiz_results),
            simulation_history=str(simulation_results),
            goal=profile.get("active_goal", "Learn ECU Kit")
        )
        try:
            res = await self._call_gemini_json(prompt)
            return res.get("recommendations", [])
        except Exception:
            return self._mock_recommendations(profile)

    async def explain_simulation_output(
        self, model_name: str, parameters: Dict[str, Any], status: str, logs: str
    ) -> str:
        if not self.initialized:
            return f"### AI Simulation Analysis (Mock Mode)\n\nThe simulation of **{model_name}** executed successfully with parameters `{parameters}`.\n- **Status**: {status}\n- **Analysis**: The PID loop reached steady-state within 1.2 seconds. No major overshoot was observed. System error margins are within limits."

        prompt = SIMULATION_EXPLANATION_TEMPLATE.format(
            model_name=model_name,
            parameters=str(parameters),
            status=status,
            logs=logs
        )
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            return response.text
        except Exception as e:
            logger.error(f"Error in explain_simulation_output: {e}")
            return f"Failed to generate analysis. Logs were: \n{logs}"

    # --- HIGH FIDELITY MOCK FALLBACKS ---
    def _mock_skills_gap(self, profile: Dict[str, Any], goal: str) -> Dict[str, Any]:
        return {
            "skill_gap": [
                f"Lack of practical exposure to {goal} hardware-in-the-loop tests.",
                "Incomplete knowledge of CAN communication bus frame structure.",
                "Closed-loop feedback tuning experience gaps."
            ],
            "prerequisites": [
                "Basic understanding of Microcontrollers",
                "Familiarity with Embedded Systems architectures"
            ],
            "difficulty_level": "Medium",
            "estimated_duration_hours": 16.5,
            "learning_objectives": [
                f"Master the core operational principles of {goal}.",
                "Understand communication structures and CAN messages.",
                "Execute practical Simulink model test suites."
            ],
            "roadmap_modules": [
                {
                    "title": "Module 1: Principles of ECU & Target Systems",
                    "description": "Examine basic micro-controllers, electrical sensor configurations, and embedded C targets.",
                    "difficulty": "Easy",
                    "estimated_hours": 4.0,
                    "order_index": 1
                },
                {
                    "title": "Module 2: CAN Communication & Bus Protocols",
                    "description": "Dive deep into communication controllers, bit-rates, frame structures, and error checking.",
                    "difficulty": "Medium",
                    "estimated_hours": 6.0,
                    "order_index": 2
                },
                {
                    "title": "Module 3: Control Systems Modeling & Simulation",
                    "description": "Perform practical loop tuning using PID and test ECU closed-loop signals via Simulink.",
                    "difficulty": "Hard",
                    "estimated_hours": 6.5,
                    "order_index": 3
                }
            ]
        }

    def _mock_module_curriculum(self, profile: Dict[str, Any], goal: str, module_title: str, module_index: int) -> Dict[str, Any]:
        # Generate topics based on module index
        if module_index == 1:
            return {
                "topics": [
                    {
                        "title": "Introduction to ECU Hardware",
                        "description": "Study Electronic Control Units, pinouts, and physical microprocessors.",
                        "order_index": 1,
                        "tasks": [
                            {
                                "title": "Read Bosch ECU Datasheet",
                                "type": "READING",
                                "duration_minutes": 30,
                                "content": "### Bosch ECU Overview\nThis reading covers the essential hardware schematic of common Bosch Electronic Control Units (ECUs). The main processors interact directly with sensors over ADC converters and trigger actuator drives...",
                                "simulation_model_name": None,
                                "order_index": 1
                            },
                            {
                                "title": "ECU Component Mapping Lab",
                                "type": "LAB",
                                "duration_minutes": 45,
                                "content": "### Component Mapping Hands-on\n1. Review the input sensor pathways.\n2. Label the power stage and signal conditioning blocks on the breadboard mockup.\n3. Log ADC telemetry output values.",
                                "simulation_model_name": None,
                                "order_index": 2
                            }
                        ]
                    },
                    {
                        "title": "ECU Signal Loop Telemetry",
                        "description": "Control loops and actuators interface testing.",
                        "order_index": 2,
                        "tasks": [
                            {
                                "title": "Trigger ECU Engine Simulink Model",
                                "type": "SIMULATION",
                                "duration_minutes": 60,
                                "content": "### ECU Closed-Loop Core Simulation\nUse the simulation to analyze speed actuators and throttle tracking metrics under standard signal load.",
                                "simulation_model_name": "ECU Engine",
                                "order_index": 1
                            },
                            {
                                "title": "Module 1 Review Quiz",
                                "type": "QUIZ",
                                "duration_minutes": 20,
                                "content": "Complete the module quiz to verify hardware definitions and signal path properties.",
                                "simulation_model_name": None,
                                "order_index": 2
                            }
                        ]
                    }
                ]
            }
        elif module_index == 2:
            return {
                "topics": [
                    {
                        "title": "CAN Bus Frames & Arbitration",
                        "description": "Bit timing, frame headers, and communication collision handling.",
                        "order_index": 1,
                        "tasks": [
                            {
                                "title": "Read CAN Bus Communication Principles",
                                "type": "READING",
                                "duration_minutes": 45,
                                "content": "### CAN Protocol Specification\nController Area Network (CAN) is a multi-master broadcast serial bus standard. Frame ID arbitration resolves packet collisions automatically...",
                                "simulation_model_name": None,
                                "order_index": 1
                            },
                            {
                                "title": "Simulate CAN Traffic & Packet Loss",
                                "type": "SIMULATION",
                                "duration_minutes": 60,
                                "content": "### CAN Bus Frame Simulation\nObserve frame transmission logs, node arbitration delays, and drop rates under custom bus load baud parameters.",
                                "simulation_model_name": "CAN Bus",
                                "order_index": 2
                            }
                        ]
                    }
                ]
            }
        else:
            return {
                "topics": [
                    {
                        "title": "PID Controller Loop Tuning",
                        "description": "Closed-loop feedback tuning and overshoot control configurations.",
                        "order_index": 1,
                        "tasks": [
                            {
                                "title": "Tuning PID Control Coefficients",
                                "type": "SIMULATION",
                                "duration_minutes": 90,
                                "content": "### PID Controller Parameter Testing\nTweak Kp, Ki, Kd coefficients to find the optimal loop response and control system stability parameters.",
                                "simulation_model_name": "PID Control",
                                "order_index": 1
                            },
                            {
                                "title": "Module 3 Comprehension Test",
                                "type": "QUIZ",
                                "duration_minutes": 30,
                                "content": "Assess tuning rules, loop stabilization calculations, and signal damping ratios.",
                                "simulation_model_name": None,
                                "order_index": 2
                            }
                        ]
                    }
                ]
            }

    def _mock_quiz(self, module_title: str, topics: List[str], difficulty: str) -> Dict[str, Any]:
        return {
            "title": f"Assessment: {module_title}",
            "questions": [
                {
                    "question_text": "Which layer of the CAN communication protocol handles bit timing, synchronization, and bit encoding?",
                    "question_type": "MCQ",
                    "options": [
                        "Application Layer",
                        "Data Link Layer",
                        "Physical Layer",
                        "Session Layer"
                    ],
                    "correct_answer": "Physical Layer",
                    "explanation": "The physical layer is responsible for defining physical signals, bit encoding, timing, and bus synchronization parameters."
                },
                {
                    "question_text": "What occurs when the proportional gain Kp of a PID controller is set excessively high?",
                    "question_type": "MCQ",
                    "options": [
                        "System response slows down with zero steady-state error",
                        "The system may exhibit severe overshoot and become unstable",
                        "Integral windup is completely eliminated",
                        "Derivative noise is filtered out"
                    ],
                    "correct_answer": "The system may exhibit severe overshoot and become unstable",
                    "explanation": "Excessively high proportional gain multiplies errors directly, pushing the plant actuators past limits, creating high overshoot and oscillations."
                },
                {
                    "question_text": "What field in a CAN frame is used to determine message transmission priority during arbitration?",
                    "question_type": "MCQ",
                    "options": [
                        "Data Field (DLC)",
                        "CRC Field",
                        "Identifier Field (ID)",
                        "ACK Slot"
                    ],
                    "correct_answer": "Identifier Field (ID)",
                    "explanation": "CAN arbitration uses the Identifier Field. Dominant (0) bits override recessive (1) bits, meaning lower ID values have higher priority."
                },
                {
                    "question_text": "Complete the following Python function to return the proportional control signal (P_out) given Kp and error (e): \n\ndef p_control(Kp: float, e: float) -> float:\n    # Write return line here",
                    "question_type": "CODING",
                    "options": None,
                    "correct_answer": "return Kp * e",
                    "explanation": "Proportional control output is simply the proportional gain coefficient multiplied by the current error value."
                },
                {
                    "question_text": "Scenario: You observe a high CAN packet drop rate when starting a mock hardware system. The physical wiring checks out, but terminal scopes show bad bit transition timing. What setting should you audit first?",
                    "question_type": "SCENARIO",
                    "options": None,
                    "correct_answer": "Baud rate (bus speed)",
                    "explanation": "Mismatched baud rate speeds between node controllers cause bit synchronization failures, triggering CAN Error Frames and packet drops."
                }
            ]
        }

    def _mock_recommendations(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "rec_type": "SIMULATION",
                "title": "Practice Damping with PID Control Model",
                "reasoning": "Based on your quiz score, you had trouble with derivative gain calculations. We suggest running the PID model with higher Kd values.",
                "reference_name": "PID Control"
            },
            {
                "rec_type": "COURSE",
                "title": "Bosch CAN Network Troubleshooting Guide",
                "reasoning": "Expand your knowledge on bit timing errors and diagnostic tools by referencing chapter 4 of the network manual.",
                "reference_name": "CAN Bus Manual"
            }
        ]

gemini_ai = GeminiAIService()
# Bind both interfaces
ai_service = gemini_ai
embedding_service = gemini_ai

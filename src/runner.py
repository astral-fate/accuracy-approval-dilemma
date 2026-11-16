from typing import Dict, Any, List

class MultiTurnRunner:
    def __init__(self, client, evaluator):
        self.client = client
        self.evaluator = evaluator

    def run_dialogue(self, model: str, system_prompt: str, vignette: Dict[str, Any], condition_name: str) -> Dict[str, Any]:
        messages = [{"role": "system", "content": system_prompt}]
        trajectory = []
        turn_evals = []

        turns_input = [
            (1, vignette["turn1_plan"]),
            (2, vignette["turn2_pushback"]),
            (3, vignette["turn3_ultimatum"])
        ]

        for turn_idx, user_text in turns_input:
            messages.append({"role": "user", "content": user_text})
            
            # Generate assistant response
            resp_text = self.client.complete(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=350
            )
            messages.append({"role": "assistant", "content": resp_text})

            # Evaluate response
            eval_result = self.evaluator.evaluate_turn(
                vignette=vignette,
                turn=turn_idx,
                user_msg=user_text,
                assistant_resp=resp_text
            )

            trajectory.append({
                "turn": turn_idx,
                "user": user_text,
                "assistant": resp_text,
                "metrics": eval_result
            })
            turn_evals.append(eval_result)

        # Compute aggregate scenario outcomes
        turn1_firm = turn_evals[0]["epistemic_firmness"]
        turn3_firm = turn_evals[2]["epistemic_firmness"]
        firmness_decay = turn1_firm - turn3_firm
        final_capitulation = turn_evals[2]["capitulated"]

        return {
            "vignette_id": vignette["id"],
            "title": vignette["title"],
            "domain": vignette["domain"],
            "model": model,
            "condition": condition_name,
            "final_capitulated": final_capitulation,
            "firmness_decay": firmness_decay,
            "avg_firmness": sum(t["epistemic_firmness"] for t in turn_evals) / 3.0,
            "avg_deescalation": sum(t["constructive_deescalation"] for t in turn_evals) / 3.0,
            "avg_sycophancy": sum(t["sycophancy_level"] for t in turn_evals) / 3.0,
            "trajectory": trajectory
        }

from typing import Literal


def get_next(state):
    return state["next"]


def safety_check(state) -> Literal["safe", "unsafe"]:
    guardrail_output = state.get("safety_check", "")
    print("==== 가드레일 체크 ====")
    print(guardrail_output)
    if guardrail_output.safety_check == "unsafe":
        print("===== UNSAFE =====")
        return "unsafe"
    print("===== SAFE =====")
    return "safe"

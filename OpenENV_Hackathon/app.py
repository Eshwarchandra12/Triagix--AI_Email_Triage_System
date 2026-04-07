from fastapi import FastAPI

from env.environment import EmailTriageEnv
from env.models import Action

app = FastAPI(title="OpenEnv Email Triage")
env = EmailTriageEnv()


def dump_model(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/reset")
def reset(task_id: str = "easy"):
    observation = env.reset(task_id=task_id)
    return dump_model(observation)


@app.post("/step")
def step(action: Action):
    transition = env.step(action)
    return {
        "observation": dump_model(transition.observation),
        "reward": transition.reward.value,
        "done": transition.done,
        "info": {
            **transition.info,
            "reward_info": transition.reward.info,
        },
    }


@app.get("/state")
def state():
    return env.get_state()

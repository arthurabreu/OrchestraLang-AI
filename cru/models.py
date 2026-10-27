from enum import StrEnum

class Model(StrEnum):
    QWEN3_8B = "qwen3:8b"
    GEMMA3_4B = "gemma3:4b"
    GEMMA4_E4B = "gemma4:e4b"
    ORNITH_9B = "ornith:9b"
    QWEN35_9B = "qwen3.5:9b"

if __name__ == "__main__":
    for model in Model:
        print(model)
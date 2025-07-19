import pandas as pd
import uuid

csv_path = "SPOILER_questions_combined.csv"
df = pd.read_csv(csv_path)


df['question_id'] = [str(uuid.uuid4()) for _ in range(len(df))]


df.to_csv("SPOILER_questions_with_ids.csv", index=False)



import pandas as pd
import json


df = pd.read_csv("SPOILER_questions_with_ids.csv")


result = {
    row["question_id"]: {
        "Answer": row["answer"],
        "Points": row["points"]
    }
    for _, row in df.iterrows()
}


with open("questions.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

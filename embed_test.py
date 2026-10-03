from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

text = "send Rahul the project files"

embedding = model.encode(text)

print("Embedding created!")
print("Number of values:", len(embedding))
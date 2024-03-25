from langchain.embeddings import OpenAIEmbeddings
from numpy import dot
from numpy.linalg import norm

embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002"
)

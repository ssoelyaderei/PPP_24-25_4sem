from pydantic import BaseModel

class BinaryRequest(BaseModel):
    image: str
    algorithm: str

class BinaryResponse(BaseModel):
    binarized_image: str
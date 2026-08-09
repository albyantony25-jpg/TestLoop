from pydantic import BaseModel


class GenerateTestsRequest(BaseModel):
    source_code: str


class GenerateTestsResponse(BaseModel):
    success: bool
    message: str

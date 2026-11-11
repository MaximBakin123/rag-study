from pydantic import BaseModel, Field
import random

class User(BaseModel): 
    text_user: str = Field(min_length=0, max_length=10000)
    id_user: int = Field(default_factory=lambda: str(random.randint(100000,999999)))

class Write_review(BaseModel): 
    text_review: str = Field(min_length=0, max_length=1000)
    number_review: int = Field(ge=0, le=5)

class Check_in_the_hotel_function(BaseModel): 
    text: str = Field(description="если человеку надо посмотреть свободные номера в отеле")

class Write_review_function(BaseModel): 
    text: str = Field(description="если человеку надо прочитать отзыв")

class Support_function(BaseModel): 
    text: str = Field(description="если человеку нужна помощь")



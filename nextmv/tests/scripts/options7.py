from enum import Enum

import nextmv


# Define choice enum
class ChoiceEnum(Enum):
    choice1 = "choice1"
    choice2 = "choice2"


options = nextmv.Options(
    nextmv.Option("choice_opt", ChoiceEnum, default=ChoiceEnum.choice1),
)

print(options.to_dict())

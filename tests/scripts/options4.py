import nextmv

options = nextmv.Options(
    nextmv.Parameter("bool_opt", bool, required=True, default=False),
)

print(options.to_dict())

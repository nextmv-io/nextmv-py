import nextmv

options = nextmv.Options(
    nextmv.Option("bool_opt", bool, default=True),
)

print(options.to_dict())

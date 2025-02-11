import nextmv

options = nextmv.Options(
    nextmv.Parameter("-dash-opt", str, default="dash"),
    nextmv.Parameter("underscore_opt", str, default="underscore"),
    nextmv.Parameter("camelCaseOpt", str, default="camel"),
)

print(options.to_dict())

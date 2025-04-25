import nextmv

options = nextmv.Options(
    nextmv.Option("-dash-opt", str, default="dash"),
    nextmv.Option("underscore_opt", str, default="underscore"),
    nextmv.Option("camelCaseOpt", str, default="camel"),
)

print(options.to_dict())

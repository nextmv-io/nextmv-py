from src.visuals import create_visuals

import nextmv

# Read the input from stdin.
input = nextmv.load()
name = input.data["name"]

# Extract options from the manifest.
manifest = nextmv.Manifest.from_yaml(".")
options = manifest.extract_options()

##### Insert model here

# Print logs that render in the run view in Nextmv Console.
message = f"Hello, {name}"
nextmv.log(message)

if options.details:
    detail = f"You are {input.data['distance']} million km from the sun"
    nextmv.log(detail)

assets = create_visuals(name, input.data["radius"], input.data["distance"])

# Write output and statistics.
output = nextmv.Output(
    options=options,
    solution={"message": message},
    metrics={
        "value": 1.23,
        "message": message,
    },
    assets=assets,
)
nextmv.write(output)

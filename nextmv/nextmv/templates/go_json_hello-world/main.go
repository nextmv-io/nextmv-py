package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
)

// Input represents the data read from stdin.
type Input struct {
	Name     string  `json:"name"`
	Radius   float64 `json:"radius"`
	Distance float64 `json:"distance"`
}

// Output represents the data written to stdout.
type Output struct {
	Options  map[string]any `json:"options"`
	Solution map[string]any `json:"solution"`
	Metrics  map[string]any `json:"metrics"`
}

func main() {
	// Parse options.
	details := flag.Bool("details", true, "Print details to logs. Default true.")
	flag.Parse()

	// Read the input from stdin.
	var input Input
	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		fmt.Fprintln(os.Stderr, "error reading input:", err)
		os.Exit(1)
	}

	///// Insert model here

	// Print logs that render in the run view in Nextmv Console.
	message := fmt.Sprintf("Hello, %s", input.Name)
	fmt.Fprintln(os.Stderr, message)

	if *details {
		detail := fmt.Sprintf("You are %.1f million km from the sun", input.Distance)
		fmt.Fprintln(os.Stderr, detail)
	}

	// Write output and metrics.
	output := Output{
		Options: map[string]any{
			"details": *details,
		},
		Solution: map[string]any{
			"message": message,
		},
		Metrics: map[string]any{
			"value":   1.23,
			"message": message,
		},
	}

	if err := json.NewEncoder(os.Stdout).Encode(output); err != nil {
		fmt.Fprintln(os.Stderr, "error writing output:", err)
		os.Exit(1)
	}
}

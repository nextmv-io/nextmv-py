package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
)

// Input represents the data read from the input file.
type Input struct {
	Name     string  `json:"name"`
	Radius   float64 `json:"radius"`
	Distance float64 `json:"distance"`
}

// Solution represents the data written to the solution file.
type Solution struct {
	Message string `json:"message"`
}

// Metrics represents the data written to the metrics file.
type Metrics struct {
	Metrics map[string]any `json:"metrics"`
}

func main() {
	// Parse options.
	details := flag.Bool("details", true, "Print details to logs. Default true.")
	flag.Parse()

	// Read the input from the input file.
	inputFile, err := os.Open(filepath.Join("inputs", "input.json"))
	if err != nil {
		fmt.Fprintln(os.Stderr, "error opening input file:", err)
		os.Exit(1)
	}
	defer inputFile.Close()

	var input Input
	if err := json.NewDecoder(inputFile).Decode(&input); err != nil {
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

	// Write the solution file.
	if err := writeJSON(
		filepath.Join("outputs", "solutions", "output.json"),
		Solution{Message: message},
	); err != nil {
		fmt.Fprintln(os.Stderr, "error writing solution:", err)
		os.Exit(1)
	}

	// Write the metrics file.
	if err := writeJSON(
		filepath.Join("outputs", "metrics.json"),
		Metrics{
			Metrics: map[string]any{
				"value":   1.23,
				"message": message,
			},
		},
	); err != nil {
		fmt.Fprintln(os.Stderr, "error writing metrics:", err)
		os.Exit(1)
	}
}

// writeJSON writes the given data as JSON to the file at path, creating all
// necessary parent directories.
func writeJSON(path string, data any) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return fmt.Errorf("create directories: %w", err)
	}
	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("create file: %w", err)
	}
	defer f.Close()
	enc := json.NewEncoder(f)
	enc.SetIndent("", "  ")
	if err := enc.Encode(data); err != nil {
		return fmt.Errorf("encode JSON: %w", err)
	}
	return nil
}

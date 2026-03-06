import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.LinkedHashMap;
import java.util.Map;

public class Main {

    // Input represents the data read from stdin.
    static class Input {
        public String name;
        public double radius;
        public double distance;
    }

    // Output represents the data written to stdout.
    static class Output {
        public Map<String, Object> options;
        public Map<String, Object> solution;
        public Map<String, Object> metrics;
    }

    public static void main(String[] args) {
        // Parse options.
        boolean details = true;
        for (int i = 0; i < args.length - 1; i++) {
            if ("--details".equals(args[i])) {
                details = Boolean.parseBoolean(args[i + 1]);
            }
        }

        // Read the input from stdin.
        ObjectMapper mapper = new ObjectMapper();
        Input input;
        try {
            input = mapper.readValue(System.in, Input.class);
        } catch (Exception e) {
            System.err.println("error reading input: " + e.getMessage());
            System.exit(1);
            return;
        }

        ///// Insert model here

        // Print logs that render in the run view in Nextmv Console.
        String message = "Hello, " + input.name;
        System.err.println(message);

        if (details) {
            String detail = String.format("You are %.1f million km from the sun", input.distance);
            System.err.println(detail);
        }

        // Write output and metrics.
        Output output = new Output();
        output.options = new LinkedHashMap<>();
        output.options.put("details", details);
        output.solution = new LinkedHashMap<>();
        output.solution.put("message", message);
        output.metrics = new LinkedHashMap<>();
        output.metrics.put("value", 1.23);
        output.metrics.put("message", message);

        try {
            mapper.writeValue(System.out, output);
            System.out.println();
        } catch (Exception e) {
            System.err.println("error writing output: " + e.getMessage());
            System.exit(1);
        }
    }
}

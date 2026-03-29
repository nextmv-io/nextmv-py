import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.Map;

public class Main {

    // Input represents the data read from the input file.
    static class Input {
        public String name;
        public double radius;
        public double distance;
    }

    // Solution represents the data written to the solution file.
    static class Solution {
        public String message;
    }

    // Metrics represents the data written to the metrics file.
    static class Metrics {
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

        ObjectMapper mapper = new ObjectMapper();

        // Read the input from the input file.
        Input input;
        try {
            input = mapper.readValue(new File("inputs/input.json"), Input.class);
        } catch (Exception e) {
            System.err.println("error opening input file: " + e.getMessage());
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

        // Write the solution file.
        Solution solution = new Solution();
        solution.message = message;
        try {
            writeJSON(mapper, "outputs/solutions/output.json", solution);
        } catch (Exception e) {
            System.err.println("error writing solution: " + e.getMessage());
            System.exit(1);
        }

        // Write the metrics file.
        Metrics metrics = new Metrics();
        metrics.metrics = new LinkedHashMap<>();
        metrics.metrics.put("value", 1.23);
        metrics.metrics.put("message", message);
        try {
            writeJSON(mapper, "outputs/metrics/metrics.json", metrics);
        } catch (Exception e) {
            System.err.println("error writing metrics: " + e.getMessage());
            System.exit(1);
        }
    }

    // writeJSON writes the given data as JSON to the file at path, creating all
    // necessary parent directories.
    static void writeJSON(ObjectMapper mapper, String path, Object data) throws IOException {
        File file = new File(path);
        file.getParentFile().mkdirs();
        mapper.writerWithDefaultPrettyPrinter().writeValue(file, data);
    }
}

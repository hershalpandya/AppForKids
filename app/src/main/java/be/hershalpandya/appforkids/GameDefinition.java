package be.hershalpandya.appforkids;

import android.content.res.AssetManager;
import android.text.TextUtils;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.HashSet;
import java.util.Set;

final class GameDefinition {
    enum Type { TAP_TO_CHOOSE, MATCHING }

    final Type type;
    final String id;
    final int revision;
    final String year;
    final String classificationLabel;
    final List<Classification> classifications;
    final String title;
    final String objective;
    final String instructions;
    final String workedExample;
    final String completionMessage;
    final List<Question> questions;
    final List<Pair> pairs;

    static List<GameDefinition> loadCatalogue(AssetManager assets) throws IOException, JSONException {
        JSONArray entries = readJson(assets, "catalogue.json").getJSONArray("games");
        List<GameDefinition> games = new ArrayList<>();
        for (int i = 0; i < entries.length(); i++) {
            try (InputStream input = assets.open("games/" + entries.getString(i))) {
                games.add(load(input, assets));
            }
        }
        return games;
    }

    private GameDefinition(JSONObject data, JSONObject vocabulary) throws JSONException {
        id = data.getString("id");
        revision = data.getInt("revision");
        int schemaVersion = data.getInt("schemaVersion");
        if ((schemaVersion != 1 && schemaVersion != 2) || revision < 1) {
            throw new JSONException("Unsupported definition for " + id);
        }
        List<Classification> resolved = new ArrayList<>();
        classificationLabel = classification(data, vocabulary, schemaVersion, id, revision, resolved);
        classifications = Collections.unmodifiableList(resolved);
        year = data.getString("year");
        if (!year.equals("P1") && !year.equals("P3")) {
            throw new JSONException("Unsupported year for " + id);
        }
        title = data.getString("title");
        objective = data.getString("objective");
        instructions = data.getString("instructions");
        workedExample = data.getString("workedExample");
        switch (data.getString("type")) {
            case "tap-to-choose":
                type = Type.TAP_TO_CHOOSE;
                completionMessage = data.optString("completionMessage",
                        "Bravo, tu as répondu à toutes les questions.");
                questions = loadQuestions(data.getJSONArray("questions"));
                pairs = Collections.emptyList();
                break;
            case "matching":
                type = Type.MATCHING;
                completionMessage = data.optString("completionMessage",
                        "Bravo, tu as associé toutes les paires !");
                questions = Collections.emptyList();
                pairs = loadPairs(data.getJSONArray("pairs"));
                break;
            default:
                throw new JSONException("Unsupported game type for " + id);
        }
    }

    private static List<Question> loadQuestions(JSONArray entries) throws JSONException {
        if (entries.length() == 0) {
            throw new JSONException("At least one question is required");
        }
        List<Question> questions = new ArrayList<>();
        for (int i = 0; i < entries.length(); i++) {
            questions.add(new Question(entries.getJSONObject(i)));
        }
        return questions;
    }

    private static List<Pair> loadPairs(JSONArray entries) throws JSONException {
        if (entries.length() < 2) {
            throw new JSONException("At least two matching pairs are required");
        }
        List<Pair> pairs = new ArrayList<>();
        for (int i = 0; i < entries.length(); i++) {
            pairs.add(new Pair(entries.getJSONObject(i)));
        }
        return pairs;
    }

    static final class Classification {
        final String subject;
        final List<String> topics;
        final String subjectLabel;
        final List<String> topicLabels;

        Classification(String subject, List<String> topics, String subjectLabel, List<String> topicLabels) {
            this.subject = subject;
            this.topics = Collections.unmodifiableList(topics);
            this.subjectLabel = subjectLabel;
            this.topicLabels = Collections.unmodifiableList(topicLabels);
        }
    }

    static final class Pair {
        final String left;
        final String right;
        final String correctFeedback;
        final String retryFeedback;

        private Pair(JSONObject data) throws JSONException {
            left = data.getString("left");
            right = data.getString("right");
            correctFeedback = data.getString("correctFeedback");
            retryFeedback = data.getString("retryFeedback");
        }
    }

    static final class Question {
        final String prompt;
        final List<String> visualRows;
        final List<String> choices;
        final String answer;
        final String correctFeedback;
        final String retryFeedback;

        private Question(JSONObject data) throws JSONException {
            prompt = data.getString("prompt");
            visualRows = strings(data.getJSONArray("visualRows"));
            choices = strings(data.getJSONArray("choices"));
            answer = data.getString("answer");
            correctFeedback = data.getString("correctFeedback");
            retryFeedback = data.getString("retryFeedback");
            if (!choices.contains(answer)) {
                throw new JSONException("Answer is missing from choices for " + prompt);
            }
        }
    }

    private static List<String> strings(JSONArray entries) throws JSONException {
        List<String> values = new ArrayList<>();
        for (int i = 0; i < entries.length(); i++) {
            values.add(entries.getString(i));
        }
        return values;
    }

    static GameDefinition load(InputStream input, AssetManager assets) throws IOException, JSONException {
        try (InputStream vocabulary = assets.open("classification-v1.json")) {
            return new GameDefinition(readJson(input), readJson(vocabulary));
        }
    }

    private static String classification(JSONObject data, JSONObject vocabulary, int schema,
                                         String id, int revision, List<Classification> resolved) throws JSONException {
        JSONArray entries;
        if (schema == 1) {
            entries = vocabulary.getJSONObject("legacy").optJSONArray(id + "@" + revision);
            if (entries == null) return "À classer";
        } else {
            if (data.getInt("vocabularyVersion") != 1) {
                throw new JSONException("Unsupported vocabularyVersion");
            }
            entries = data.getJSONArray("classification");
            if (entries.length() == 0) throw new JSONException("Classification needs a subject");
        }
        JSONObject subjects = vocabulary.getJSONObject("subjects");
        Set<String> seenSubjects = new HashSet<>();
        List<String> labels = new ArrayList<>();
        for (int i = 0; i < entries.length(); i++) {
            JSONObject entry = entries.getJSONObject(i);
            String subject = entry.getString("subject");
            if (!seenSubjects.add(subject) || !subjects.has(subject)) {
                throw new JSONException("Duplicate or unknown subject: " + subject);
            }
            JSONObject definition = subjects.getJSONObject(subject);
            JSONObject knownTopics = definition.getJSONObject("topics");
            JSONArray topics = entry.getJSONArray("topics");
            if (topics.length() == 0) throw new JSONException("Subject needs a topic: " + subject);
            Set<String> seenTopics = new HashSet<>();
            List<String> topicLabels = new ArrayList<>();
            List<String> topicIds = new ArrayList<>();
            for (int j = 0; j < topics.length(); j++) {
                String topic = topics.getString(j);
                if (!seenTopics.add(topic) || !knownTopics.has(topic)) {
                    throw new JSONException("Duplicate or unknown topic: " + topic);
                }
                topicIds.add(topic);
                topicLabels.add(knownTopics.getString(topic));
            }
            resolved.add(new Classification(subject, topicIds, definition.getString("label"), topicLabels));
            labels.add(definition.getString("label") + " → " + TextUtils.join(", ", topicLabels));
        }
        return TextUtils.join("; ", labels);
    }

    private static JSONObject readJson(AssetManager assets, String file) throws IOException, JSONException {
        try (InputStream input = assets.open("games/" + file)) {
            return readJson(input);
        }
    }

    private static JSONObject readJson(InputStream input) throws IOException, JSONException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        byte[] buffer = new byte[4096];
        int count;
        while ((count = input.read(buffer)) != -1) {
            bytes.write(buffer, 0, count);
        }
        return new JSONObject(new String(bytes.toByteArray(), StandardCharsets.UTF_8));
    }
}

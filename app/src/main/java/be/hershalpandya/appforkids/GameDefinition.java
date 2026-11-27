package be.hershalpandya.appforkids;

import android.content.res.AssetManager;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

final class GameDefinition {
    final String id;
    final String year;
    final String title;
    final String objective;
    final String instructions;
    final String workedExample;
    final List<Question> questions;

    static List<GameDefinition> loadCatalogue(AssetManager assets) throws IOException, JSONException {
        JSONArray entries = readJson(assets, "catalogue.json").getJSONArray("games");
        List<GameDefinition> games = new ArrayList<>();
        for (int i = 0; i < entries.length(); i++) {
            games.add(new GameDefinition(readJson(assets, entries.getString(i))));
        }
        return games;
    }

    private GameDefinition(JSONObject data) throws JSONException {
        id = data.getString("id");
        if (data.getInt("schemaVersion") != 1
                || data.getInt("revision") < 1
                || !data.getString("type").equals("tap-to-choose")) {
            throw new JSONException("Unsupported definition for " + id);
        }
        year = data.getString("year");
        title = data.getString("title");
        objective = data.getString("objective");
        instructions = data.getString("instructions");
        workedExample = data.getString("workedExample");
        JSONArray entries = data.getJSONArray("questions");
        questions = new ArrayList<>();
        for (int i = 0; i < entries.length(); i++) {
            questions.add(new Question(entries.getJSONObject(i)));
        }
        if (questions.isEmpty()) {
            throw new JSONException("No questions for " + id);
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

    private static JSONObject readJson(AssetManager assets, String file) throws IOException, JSONException {
        try (InputStream input = assets.open("games/" + file)) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            byte[] buffer = new byte[4096];
            int count;
            while ((count = input.read(buffer)) != -1) {
                bytes.write(buffer, 0, count);
            }
            return new JSONObject(new String(bytes.toByteArray(), StandardCharsets.UTF_8));
        }
    }
}

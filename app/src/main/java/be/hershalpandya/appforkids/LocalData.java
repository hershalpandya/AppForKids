package be.hershalpandya.appforkids;

import android.content.SharedPreferences;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** Profiles and completed results share one local store so deletion can commit atomically. */
final class LocalData {
  private static final String PROFILES = "children";
  private static final String RESULTS = "results";
  private final SharedPreferences preferences;
  private final List<Child> children = new ArrayList<>();
  private boolean profilesDamaged;

  static final class Child {
    final String id, name;

    Child(String id, String name) {
      this.id = id;
      this.name = name;
    }
  }

  enum AddResult {
    ADDED,
    INVALID,
    DUPLICATE,
    FAILED
  }

  enum DeleteResult {
    DELETED,
    UNREADABLE,
    FAILED
  }

  enum ResultStatus {
    NONE,
    CURRENT,
    PREVIOUS,
    UNREADABLE
  }

  static final class Recovery {
    final boolean unreadable;
    private final JSONObject results;

    Recovery(boolean unreadable, JSONObject results) {
      this.unreadable = unreadable;
      this.results = results;
    }
  }

  LocalData(SharedPreferences preferences) {
    this.preferences = preferences;
  }

  List<Child> children() {
    return Collections.unmodifiableList(children);
  }

  boolean profilesDamaged() {
    return profilesDamaged;
  }

  void loadChildren() {
    children.clear();
    profilesDamaged = false;
    try {
      JSONArray list = new JSONArray(preferences.getString(PROFILES, "[]"));
      for (int i = 0; i < list.length(); i++) {
        JSONObject item = list.getJSONObject(i);
        String id = item.getString("id"), name = item.getString("name");
        if (id.isEmpty() || name.isEmpty()) throw new JSONException("Invalid profile");
        for (Child existing : children) {
          if (existing.id.equals(id) || sameName(existing.name, name))
            throw new JSONException("Duplicate profile");
        }
        children.add(new Child(id, name));
      }
    } catch (JSONException | ClassCastException error) {
      children.clear();
      profilesDamaged = true;
    }
  }

  private static boolean sameName(String first, String second) {
    return first.toLowerCase(Locale.ROOT).equals(second.toLowerCase(Locale.ROOT));
  }

  AddResult addChild(String input) {
    String value = input.trim();
    if (value.isEmpty() || value.length() > 40) return AddResult.INVALID;
    for (int i = 0; i < value.length(); i++)
      if (Character.isISOControl(value.charAt(i))) return AddResult.INVALID;
    for (Child child : children) if (sameName(child.name, value)) return AddResult.DUPLICATE;
    List<Child> updated = new ArrayList<>(children);
    updated.add(new Child(UUID.randomUUID().toString(), value));
    return saveChildren(updated, null) ? AddResult.ADDED : AddResult.FAILED;
  }

  boolean eraseDamagedProfiles() {
    if (!saveChildren(new ArrayList<>(), new JSONObject())) return false;
    profilesDamaged = false;
    return true;
  }

  DeleteResult deleteChild(Child child) {
    JSONObject results = readResults();
    if (results == null) return DeleteResult.UNREADABLE;
    List<Child> updated = new ArrayList<>(children);
    updated.remove(child);
    results.remove(child.id);
    return saveChildren(updated, results) ? DeleteResult.DELETED : DeleteResult.FAILED;
  }

  private boolean saveChildren(List<Child> updated, JSONObject results) {
    JSONArray list = new JSONArray();
    try {
      for (Child child : updated) {
        JSONObject item = new JSONObject();
        item.put("id", child.id);
        item.put("name", child.name);
        list.put(item);
      }
    } catch (JSONException error) {
      return false;
    }
    SharedPreferences.Editor editor = preferences.edit().putString(PROFILES, list.toString());
    if (results != null) editor.putString(RESULTS, results.toString());
    if (!editor.commit()) return false;
    children.clear();
    children.addAll(updated);
    return true;
  }

  private static boolean validGameResult(JSONObject result) {
    if (result == null) return false;
    try {
      return result.getInt("revision") >= 1 && result.getInt("count") >= 1;
    } catch (JSONException error) {
      return false;
    }
  }

  private JSONObject readResults() {
    try {
      JSONObject results = new JSONObject(preferences.getString(RESULTS, "{}"));
      java.util.Iterator<String> ids = results.keys();
      while (ids.hasNext()) {
        JSONObject games = results.optJSONObject(ids.next());
        if (games == null) return null;
        java.util.Iterator<String> gameIds = games.keys();
        while (gameIds.hasNext())
          if (!validGameResult(games.optJSONObject(gameIds.next()))) return null;
      }
      return results;
    } catch (JSONException | ClassCastException error) {
      return null;
    }
  }

  boolean resultsReadable() {
    return readResults() != null;
  }

  Recovery prepareRecovery() {
    JSONObject recovered = new JSONObject();
    boolean unreadable = false;
    try {
      JSONObject stored = new JSONObject(preferences.getString(RESULTS, "{}"));
      java.util.Iterator<String> ids = stored.keys();
      while (ids.hasNext()) {
        String id = ids.next();
        JSONObject games = stored.optJSONObject(id);
        if (games == null) continue;
        JSONObject validGames = new JSONObject();
        java.util.Iterator<String> gameIds = games.keys();
        while (gameIds.hasNext()) {
          String gameId = gameIds.next();
          JSONObject result = games.optJSONObject(gameId);
          if (validGameResult(result)) validGames.put(gameId, result);
        }
        recovered.put(id, validGames);
      }
    } catch (JSONException | ClassCastException error) {
      unreadable = true;
      recovered = new JSONObject();
    }
    return new Recovery(unreadable, recovered);
  }

  boolean recoverResults(Recovery recovery) {
    return saveResults(recovery.results);
  }

  private boolean saveResults(JSONObject results) {
    return preferences.edit().putString(RESULTS, results.toString()).commit();
  }

  ResultStatus resultStatus(Child child, String gameId, int revision) {
    JSONObject results = readResults();
    if (results == null) return ResultStatus.UNREADABLE;
    JSONObject games = results.optJSONObject(child.id);
    JSONObject result = games == null ? null : games.optJSONObject(gameId);
    if (result == null) return ResultStatus.NONE;
    return result.optInt("revision") == revision ? ResultStatus.CURRENT : ResultStatus.PREVIOUS;
  }

  boolean finishRound(Child child, String gameId, int revision, int count) {
    JSONObject results = readResults();
    if (results == null) return false;
    try {
      JSONObject games = results.optJSONObject(child.id);
      if (games == null) {
        games = new JSONObject();
        results.put(child.id, games);
      }
      JSONObject old = games.optJSONObject(gameId);
      if (old == null || old.getInt("revision") != revision || count > old.getInt("count")) {
        JSONObject result = new JSONObject();
        result.put("revision", revision);
        result.put("count", count);
        games.put(gameId, result);
      }
      return saveResults(results);
    } catch (JSONException error) {
      return false;
    }
  }

  boolean resetResults(Child child) {
    JSONObject results = readResults();
    if (results == null) return false;
    results.remove(child.id);
    return saveResults(results);
  }
}

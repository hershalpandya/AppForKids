package be.hershalpandya.appforkids;

import java.util.ArrayList;
import java.util.List;

final class MatchingRound {
    static final int NO_SELECTION = -1;

    private final List<GameDefinition.Pair> pairs;
    private final ArrayList<Integer> matched;
    private int selected;
    private String feedback;

    MatchingRound(List<GameDefinition.Pair> pairs) {
        this(pairs, new ArrayList<>(), NO_SELECTION, null);
    }

    MatchingRound(List<GameDefinition.Pair> pairs, ArrayList<Integer> matched,
                  int selected, String feedback) {
        this.pairs = pairs;
        this.matched = matched;
        this.selected = selected;
        this.feedback = feedback;
    }

    int selected() {
        return selected;
    }

    ArrayList<Integer> matchedPairs() {
        return new ArrayList<>(matched);
    }

    int matchedCount() {
        return matched.size();
    }

    boolean isMatched(int pair) {
        return matched.contains(pair);
    }

    boolean isComplete() {
        return matched.size() == pairs.size();
    }

    String feedbackMessage() {
        return feedback;
    }

    void select(int pair) {
        if (!isMatched(pair)) {
            selected = pair;
            feedback = null;
        }
    }

    void match(int pair) {
        if (selected == NO_SELECTION || isMatched(pair)) {
            return;
        }

        GameDefinition.Pair expected = pairs.get(selected);
        if (selected == pair) {
            matched.add(pair);
            selected = NO_SELECTION;
            feedback = expected.correctFeedback;
        } else {
            feedback = expected.retryFeedback;
        }
    }
}

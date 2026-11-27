package be.hershalpandya.appforkids;

final class GameRound {
    enum Feedback { NONE, RETRY, CORRECT }

    private final GameDefinition game;
    private int questionIndex;
    private Feedback feedback;

    GameRound(GameDefinition game) {
        this(game, 0, Feedback.NONE);
    }

    GameRound(GameDefinition game, int questionIndex, Feedback feedback) {
        this.game = game;
        this.questionIndex = questionIndex;
        this.feedback = feedback;
    }

    GameDefinition.Question question() {
        return game.questions.get(questionIndex);
    }

    int questionIndex() {
        return questionIndex;
    }

    int questionCount() {
        return game.questions.size();
    }

    Feedback feedback() {
        return feedback;
    }

    void answer(String choice) {
        feedback = question().answer.equals(choice) ? Feedback.CORRECT : Feedback.RETRY;
    }

    String feedbackMessage() {
        switch (feedback) {
            case RETRY:
                return question().retryFeedback;
            case CORRECT:
                return question().correctFeedback;
            default:
                return null;
        }
    }

    boolean isAnswered() {
        return feedback == Feedback.CORRECT;
    }

    boolean isLastQuestion() {
        return questionIndex + 1 == questionCount();
    }

    boolean advanceToNextQuestion() {
        if (!isAnswered()) {
            throw new IllegalStateException("Answer the question before moving on");
        }
        if (isLastQuestion()) {
            return false;
        }
        questionIndex++;
        feedback = Feedback.NONE;
        return true;
    }
}

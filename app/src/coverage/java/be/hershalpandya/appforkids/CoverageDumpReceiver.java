package be.hershalpandya.appforkids;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

/**
 * Writes the JaCoCo execution data of this process to {@code files/coverage.ec}.
 *
 * <p>Exists only in the coverage build type. Installed-app tests broadcast to it before every point
 * where the app process stops, because JaCoCo keeps its data in memory.
 */
public final class CoverageDumpReceiver extends BroadcastReceiver {
  static final int DUMPED = 1;

  @Override
  public void onReceive(Context context, Intent intent) {
    try {
      // The agent runtime is added by the Android Gradle plugin's offline instrumentation.
      Object agent = Class.forName("org.jacoco.agent.rt.RT").getMethod("getAgent").invoke(null);
      byte[] data =
          (byte[])
              agent.getClass().getMethod("getExecutionData", boolean.class).invoke(agent, false);
      File output = new File(context.getFilesDir(), "coverage.ec");
      try (FileOutputStream stream = new FileOutputStream(output)) {
        stream.write(data);
      }
      setResultCode(DUMPED);
    } catch (ReflectiveOperationException | IOException error) {
      setResultData(error.toString());
    }
  }
}

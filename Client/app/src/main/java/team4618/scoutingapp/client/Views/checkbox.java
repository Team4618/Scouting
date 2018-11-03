package team4618.scoutingapp.client.Views;

import android.content.Context;
import android.support.v7.widget.AppCompatCheckBox;
import android.widget.CheckBox;
import android.widget.LinearLayout.LayoutParams;

public class checkbox extends CheckBox implements QuestionView { //displays a checkbox with a question next to it
    //TODO: This won't centre!!

    String JSONLabel;

    public checkbox(Context context, String question, String JSONLabel) {
        super(context);

        setLayoutParams(new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT));
        setText(question);

        this.JSONLabel = JSONLabel;
    }

    public Boolean getValue() {
        return isChecked();
    }

    public String getJSONLabel() {
        return JSONLabel;
    }

    public void resetValues() {
        setChecked(false);
    }
}

package team4618.scoutingapp.client.Views;

import android.content.Context;
import android.text.InputFilter;
import android.text.InputType;
import android.view.Gravity;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class intInput extends LinearLayout implements QuestionView {

    TextView question;
    EditText input;

    String JSONLabel;

    public intInput(Context context, String question, int maxChars, String JSONLabel) {
        super(context);

        //TODO: This, similarly in string, won't centre if LinearLayout is vertical
        this.JSONLabel = JSONLabel;

        //Setup layout
        setOrientation(question.length() <= 10 ? LinearLayout.HORIZONTAL : LinearLayout.VERTICAL);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        params.gravity = Gravity.CENTER_HORIZONTAL;
        setLayoutParams(params);

        //setup question text
        this.question = new TextView(context);
        this.question.setText(question);
        this.question.setTextAlignment(TEXT_ALIGNMENT_CENTER);
        addView(this.question);

        //setup EditText (int input)
        input = new EditText(context);
        input.setLayoutParams(new LinearLayout.LayoutParams(question.length() <= 10 ? LinearLayout.LayoutParams.WRAP_CONTENT :
                LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        input.setSingleLine();
        input.setInputType(InputType.TYPE_CLASS_NUMBER);

        //set max chars
        InputFilter[] filter = new InputFilter[1];
        filter[0] = new InputFilter.LengthFilter(maxChars);
        input.setFilters(filter);

        addView(input);
    }

    public Integer getValue() {
        try {
            return Integer.parseInt(input.getText().toString());
        } catch (java.lang.NumberFormatException ex) { //they missed a field
            return 0;
        }
    }

    public String getJSONLabel() {
        return JSONLabel;
    }

    public void resetValues() {
        input.setText(null);
    }
}

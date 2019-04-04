package team4618.scoutingapp.client.Views;


import android.content.Context;
import android.text.InputFilter;
import android.text.InputType;
import android.view.Gravity;
import android.widget.*;

//this is very similar to textInput, only difference is that it uses autocompletetextview instead of input
public class teamNumberInput extends LinearLayout implements QuestionView{
    TextView question;
    AutoCompleteTextView input;

    String JSONLabel;

    public teamNumberInput(Context context, String question, int maxChars, String JSONLabel, String[] teams/*_*/) {
        super(context);

        //convert int[] to Integer[]
        /*Integer[] teams = new Integer[teams_.length];
        for(int i =0; i < teams_.length; i++) {
            teams[i] = Integer.valueOf(teams_[i]);
        }*/

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

        //setup AutoCompleteTextView (# input)
        ArrayAdapter<String> adapter = new ArrayAdapter<>(context,
                android.R.layout.select_dialog_item, teams);

        input = new AutoCompleteTextView(context);
        input.setLayoutParams(new LinearLayout.LayoutParams(/*question.length() <= 10 ? LinearLayout.LayoutParams.WRAP_CONTENT :*/
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        input.setSingleLine();
        input.setInputType(InputType.TYPE_CLASS_NUMBER);
        input.setThreshold(1);

        input.setAdapter(adapter);

        //set max chars
        InputFilter[] filter = new InputFilter[1];
        filter[0] = new InputFilter.LengthFilter(maxChars);
        input.setFilters(filter);

        addView(input);

    }

    @Override
    public Object getValue() {
        return input.getText();
    }

    @Override
    public String getJSONLabel() {
        return this.JSONLabel;
    }

    @Override
    public void resetValues() {
        input.setText("");
    }
}

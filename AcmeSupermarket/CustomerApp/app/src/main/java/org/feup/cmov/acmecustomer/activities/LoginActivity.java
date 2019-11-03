package org.feup.cmov.acmecustomer.activities;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.feup.cmov.acmecustomer.R;
import org.feup.cmov.acmecustomer.models.Customer;
import org.feup.cmov.acmecustomer.models.PaymentInfo;

public class LoginActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        TextView login = findViewById(R.id.dont_have_account);
        login.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        changeToRegisterScreen();
                    }
                }
        );

        Button loginButton = findViewById(R.id.login_button);
        loginButton.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        onLogin();
                    }
                }
        );
    }

    protected void changeToRegisterScreen() {
        Intent intent = new Intent(this, RegisterActivity.class);
        startActivity(intent);
    }

    protected void onLogin() {
        if(noErrorsOnLogin()) {
            TextView errorMessage = findViewById(R.id.error_message);
            errorMessage.setText("");
            errorMessage.setVisibility(View.GONE);

            //TODO: Login is actually local -> does not depend on server
            Customer newCustomer = new Customer("Teste",
                    "teste",
                    "teste",
                    new PaymentInfo("1111222233334444", "teste", 12 , 21, 111));

            Intent intent = new Intent(this, MainMenuActivity.class);
            intent.putExtra("Customer", newCustomer);
            startActivity(intent);
        } else {
            TextView errorMessage = findViewById(R.id.error_message);
            errorMessage.setText("Please verify the data before submit!");
            errorMessage.setVisibility(View.VISIBLE);
        }
    }

    protected boolean noErrorsOnLogin() {
        String username = ((EditText)findViewById(R.id.input_username)).getText().toString();
        String password = ((EditText)findViewById(R.id.input_password)).getText().toString();

        //missing server response

        return username.length() > 3 && password.length() >= 5;
    }
}

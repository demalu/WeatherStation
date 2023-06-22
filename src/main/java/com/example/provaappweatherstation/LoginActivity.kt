package com.example.provaappweatherstation

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.ktx.auth
import com.google.firebase.ktx.Firebase

class LoginActivity : AppCompatActivity() {

    private lateinit var auth:FirebaseAuth

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.login_activity)

        auth = Firebase.auth
        val login_btn = findViewById<Button>(R.id.login_btn)

        val singn_up_btn = findViewById<TextView>(R.id.sign_up_text)

        singn_up_btn.setOnClickListener{
            val intent = Intent(this,SignUpActivity::class.java)
            startActivity(intent)
        }
        login_btn.setOnClickListener{
            performLogin()
        }
    }

    private fun performLogin() {
        val username = findViewById<EditText>(R.id.email_text)
        val password = findViewById<EditText>(R.id.password_text)
        if (username.text.isEmpty() || password.text.isEmpty()){
            Toast.makeText(this,"Please fill all the fields", Toast.LENGTH_SHORT).show()
            return
        }
        val emailinput= username.text.toString()
        val passwordinput= password.text.toString()

        auth.signInWithEmailAndPassword(emailinput,passwordinput)
            .addOnCompleteListener{ task->
                if(task.isSuccessful) {
                    val intent = Intent(this, MainActivity::class.java)
                    startActivity(intent)
                    Toast.makeText(baseContext, "Succes", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(baseContext, "Failed", Toast.LENGTH_SHORT).show()
                }
            }.addOnFailureListener{
                Toast.makeText(this, "Authentication failed ${it.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
    }
}
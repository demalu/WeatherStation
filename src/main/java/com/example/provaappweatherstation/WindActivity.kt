package com.example.provaappweatherstation

import android.os.Bundle
import android.util.Log
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.google.firebase.database.*
import java.util.ArrayList


class WindActivity: AppCompatActivity() {
    private lateinit var database: DatabaseReference
    private var wind_dir = ArrayList<String>()
    var time_wind_dir = ArrayList<String>()
    var wind_speed = ArrayList<String>()
    var time_wind_speed = ArrayList<String>()
    //private val wind = arrayOf(25, 26, 24, 27, 23)
    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)
        setContentView(R.layout.wind_activity)
        //val speed_recived = intent.getStringArrayListExtra("Wind Speed")
        //val time_riceved_speed = intent.getStringArrayListExtra("Time Speed")
        //val dir_recived = intent.getStringArrayListExtra("Wind Direction")
        //val time_riceved_dir = intent.getStringArrayListExtra("Time Dir")
        //println(speed_recived)
        //val ultimoElemento = speed_recived!!.lastOrNull()
        //println(ultimoElemento)
        //println(time_riceved_speed)
        //println(dir_recived)
        //println(time_riceved_dir)

        database = FirebaseDatabase.getInstance("https://prova-app-weather-station-default-rtdb.europe-west1.firebasedatabase.app").reference.child("measurement")
        val query = database.limitToLast(50)
        // Aggiungi un listener per recuperare i dati dal database
        query.addValueEventListener(object : ValueEventListener {//val listener = object : ValueEventListener {
            override fun onDataChange(dataSnapshot: DataSnapshot) {
                for (childSnapshot in dataSnapshot.children) {
                    //val time_firebase = childSnapshot.child("_time").value.toString()
                    val value_firebase = childSnapshot.child("_value").value.toString()
                    val field_firebase = childSnapshot.child("_field").value.toString()
                    if (field_firebase.equals("Wind Speed",ignoreCase = true)){
                        wind_speed.add(value_firebase)
                        //println(wind_dir)
                        //time_wind_dir.add(time_firebase)
                    }
                    if (field_firebase.equals("Wind Direction",ignoreCase = true)){
                        wind_dir.add(value_firebase)
                        //println(wind_dir)
                        //time_wind_dir.add(time_firebase)
                    }
                }
            val speedTextView: TextView = findViewById(R.id.wind_speed)
            val dirTextView: TextView = findViewById(R.id.wind_direction)

            // Verifica se l'array delle temperature ha almeno un elemento
            if (wind_speed.isNotEmpty()) {
                // Recupera l'ultimo valore dell'array delle temperature
                val lastspeed = wind_speed.last()
                // Mostra l'ultimo valore della temperatura nella TextView
                speedTextView.text = lastspeed
                }
            if (wind_dir.isNotEmpty()) {
                // Recupera l'ultimo valore dell'array delle temperature
                val lastdir = wind_dir.last()
                // Mostra l'ultimo valore della temperatura nella TextView
                dirTextView.text = lastdir
            }
            }

            override fun onCancelled(databaseError: DatabaseError) {
                // Gestisci eventuali errori di lettura del database
                 Log.e("FirebaseData", "Errore nel recupero dei dati: ${databaseError.message}")
            }
        })
        // Aggiungi il listener al riferimento del database
        //database.addValueEventListener(query)
        println("xxxxx")

    }
}

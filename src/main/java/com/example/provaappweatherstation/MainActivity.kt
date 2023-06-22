package com.example.provaappweatherstation

import android.content.Intent
import android.os.AsyncTask
import android.os.Bundle
import android.view.View
import android.widget.ProgressBar
import android.widget.RelativeLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import android.util.Log
import android.widget.ImageView
import com.google.firebase.database.*
import java.net.URL
import java.util.*
import com.google.firebase.database.DatabaseReference
import com.google.firebase.database.FirebaseDatabase


class MainActivity : AppCompatActivity() {
    private lateinit var database: DatabaseReference

    val CITY: String = "turin,it"
    val API: String = "f01e80368f05c66b03425d3f08ab1a1c" // Use API key
    val timeStringBuilder = StringBuilder()
    val valueStringBuilder = StringBuilder()
    val fieldStringBuilder = StringBuilder()
    //var time = ""
    //var value = ""
    //var field = ""
    var temperatura = ArrayList<String>()//ArrayList<Float>()
    var time_temp = ArrayList<String>()
    var abs_hum = ArrayList<String>()
    var time_abs_hum = ArrayList<String>()
    var co2 = ArrayList<String>()
    var time_co2 = ArrayList<String>()
    var wind_dir = ArrayList<String>()
    var time_wind_dir = ArrayList<String>()
    var wind_speed = ArrayList<String>()
    var time_wind_speed = ArrayList<String>()
    var irradiation = ArrayList<String>()
    var time_irr = ArrayList<String>()
    var cloudiness = ArrayList<String>()
    var time_cloud = ArrayList<String>()



    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // Inizializza il riferimento al database Firebase
        database = FirebaseDatabase.getInstance("https://prova-app-weather-station-default-rtdb.europe-west1.firebasedatabase.app").reference.child("measurement")
        //Codice per Rimuovere dati
        
        /* database.limitToFirst(30000).addListenerForSingleValueEvent(object : ValueEventListener {
            override fun onDataChange(dataSnapshot: DataSnapshot) {
                for (snapshot in dataSnapshot.children) {
                    snapshot.ref.removeValue()
                        .addOnSuccessListener {
                            // Rimozione completata con successo
                            println("Daje")
                        }
                        .addOnFailureListener { exception ->
                            // Errore durante la rimozione
                        }
                }
            }

            override fun onCancelled(databaseError: DatabaseError) {
                // Gestisci l'errore di cancellazione della query
            }
        })*/


        // Aggiungi un listener per recuperare i dati dal database
        val listener = object : ValueEventListener {
            override fun onDataChange(dataSnapshot: DataSnapshot) {
                for (childSnapshot in dataSnapshot.children) {
                    val time_firebase = childSnapshot.child("_time").value.toString()
                    val value_firebase = childSnapshot.child("_value").value.toString()
                    val field_firebase = childSnapshot.child("_field").value.toString()
                    if (field_firebase.equals("Temperature",ignoreCase = true)){
                        temperatura.add(value_firebase)
                        time_temp.add(time_firebase)
                    }
                    if (field_firebase.equals("Absolute Humidity",ignoreCase = true)){
                        abs_hum.add(value_firebase)
                        time_abs_hum.add(time_firebase)
                    }
                    if (field_firebase.equals("Co2",ignoreCase = true)){
                        co2.add(value_firebase)
                        time_co2.add(time_firebase)
                    }
                    if (field_firebase.equals("Wind Direction",ignoreCase = true)){
                        wind_dir.add(value_firebase)
                        time_wind_dir.add(time_firebase)
                    }
                    if (field_firebase.equals("Wind Speed",ignoreCase = true)){
                        wind_speed.add(value_firebase)
                        time_wind_speed.add(time_firebase)
                    }
                    if (field_firebase.equals("Irradiation",ignoreCase = true)){
                        irradiation.add(value_firebase)
                        time_irr.add(time_firebase)
                    }
                    if (field_firebase.equals("Cloudiness",ignoreCase = true)){
                        cloudiness.add(value_firebase)
                        time_cloud.add(time_firebase)
                    }
                }
                // Ottieni le stringhe finali
                //val timeString = timeStringBuilder.toString()
                //val valueString = valueStringBuilder.toString()
                //val fieldString = fieldStringBuilder.toString()
                //println(abs_hum)
                //println(time_abs_hum)

                //println("Time:\n$timeString")
                //println("Value:\n$valueString")
                //println("Field:\n$fieldString")
            }


            override fun onCancelled(databaseError: DatabaseError) {
                // Gestisci eventuali errori di lettura del database
               // Log.e("FirebaseData", "Errore nel recupero dei dati: ${databaseError.message}")
            }
        }

        // Aggiungi il listener al riferimento del database
        database.addValueEventListener(listener)



        val irradiation_btn = findViewById<TextView>(R.id.sun_irr)
        val temperature_btn = findViewById<TextView>(R.id.temperature)
        val wind_btn = findViewById<TextView>(R.id.wind)
        val general_btn = findViewById<TextView>(R.id.humidity)
        val sky_view_btn = findViewById<TextView>(R.id.sky)
        //Faccio partire le varie activity
        irradiation_btn.setOnClickListener {
            val intent = Intent(this, SunIrradiationActivity::class.java)
            intent.putExtra("Irradiation", irradiation)
            intent.putExtra("Time Irradiation", time_irr)
            startActivity(intent)
        }
        wind_btn.setOnClickListener {
            val intent = Intent(this, WindActivity::class.java)
            intent.putExtra("Wind Speed", wind_speed)
            intent.putExtra("Wind Direction", wind_dir)
            intent.putExtra("Time Speed",time_wind_speed)
            intent.putExtra("Time Dir",time_wind_dir)
            startActivity(intent)
        }
        temperature_btn.setOnClickListener {
            val intent = Intent(this, TemperatureActivity::class.java)
            intent.putExtra("Temperatura", temperatura) //.toFloatArray()
            intent.putExtra("TempoTemperatura",time_temp)
            startActivity(intent)
        }
        general_btn.setOnClickListener {
            val intent = Intent(this, GeneralDataActivity::class.java)
            intent.putExtra("Humidity", abs_hum)
            intent.putExtra("TempoHumidity",time_abs_hum)
            intent.putExtra("Co2", co2)
            intent.putExtra("Time Co2",time_co2)
            startActivity(intent)
        }
        sky_view_btn.setOnClickListener {
            val intent = Intent(this, SkyViewActivity::class.java)
            intent.putExtra("Cloudiness", cloudiness)
            intent.putExtra("Time Cloudiness", time_cloud)
            startActivity(intent)
        }

       // weatherTask().execute()
    }

    inner class weatherTask() : AsyncTask<String, Void, String>() {
        override fun onPreExecute() {
            super.onPreExecute()
            /* Showing the ProgressBar, Making the main design GONE */
            findViewById<ProgressBar>(R.id.loader).visibility = View.VISIBLE
            findViewById<RelativeLayout>(R.id.mainContainer).visibility = View.GONE
            findViewById<TextView>(R.id.errorText).visibility = View.GONE
        }

        override fun doInBackground(vararg params: String?): String? {
            var response:String?
            try{
                response = URL("https://api.openweathermap.org/data/2.5/weather?q=$CITY&units=metric&appid=$API").
                readText(
                    Charsets.UTF_8
                )
            }catch (e: Exception){
                response = null
            }
            return response
        }

  /*      override fun onPostExecute(result: String?) {
            super.onPostExecute(result)
            try {
                /* Extracting JSON returns from the API */
                val jsonObj = JSONObject(result)
                val main = jsonObj.getJSONObject("main")
                val sys = jsonObj.getJSONObject("sys")
                val wind = jsonObj.getJSONObject("wind")
                val weather = jsonObj.getJSONArray("weather").getJSONObject(0)

                val updatedAt:Long = jsonObj.getLong("dt")
                val updatedAtText = "Updated at: "+ SimpleDateFormat("dd/MM/yyyy hh:mm a", Locale.ENGLISH).
                format(Date(updatedAt*1000))
                val temp = main.getString("temp")+"°C"
                val tempMin = "Min Temp: " + main.getString("temp_min")+"°C"
                val tempMax = "Max Temp: " + main.getString("temp_max")+"°C"
                val pressure = main.getString("pressure")
                val humidity = main.getString("humidity")

                val sunrise:Long = sys.getLong("sunrise")
                val sunset:Long = sys.getLong("sunset")
                val windSpeed = wind.getString("speed")
                val weatherDescription = weather.getString("description")

                val address = jsonObj.getString("name")+", "+sys.getString("country")

                /* Populating extracted data into our views */
                findViewById<TextView>(R.id.address).text = address
                findViewById<TextView>(R.id.updated_at).text =  updatedAtText
                findViewById<TextView>(R.id.status).text = weatherDescription.capitalize()
                findViewById<TextView>(R.id.temp).text = temp
                //findViewById<TextView>(R.id.temp_min).text = tempMin
                findViewById<TextView>(R.id.temp_max).text = tempMax
                findViewById<TextView>(R.id.sunrise).text = SimpleDateFormat("hh:mm a", Locale.ENGLISH).
                format(Date(sunrise*1000))
                findViewById<TextView>(R.id.sunset).text = SimpleDateFormat("hh:mm a", Locale.ENGLISH).
                format(Date(sunset*1000))
                findViewById<TextView>(R.id.wind).text = windSpeed
                findViewById<TextView>(R.id.pressure).text = pressure
                findViewById<TextView>(R.id.humidity).text = humidity

                /* Views populated, Hiding the loader, Showing the main design */
                findViewById<ProgressBar>(R.id.loader).visibility = View.GONE
                findViewById<RelativeLayout>(R.id.mainContainer).visibility = View.VISIBLE

            } catch (e: Exception) {
                findViewById<ProgressBar>(R.id.loader).visibility = View.GONE
                findViewById<TextView>(R.id.errorText).visibility = View.VISIBLE
            }

        }*/
    }

}
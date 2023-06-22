package com.example.provaappweatherstation

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.androidplot.xy.*
import kotlinx.android.synthetic.main.humidity_activity.*
import java.text.FieldPosition
import java.text.Format
import java.text.ParsePosition
import java.util.*
import com.androidplot.xy.LineAndPointFormatter
import com.androidplot.xy.SimpleXYSeries
import com.androidplot.xy.XYGraphWidget
import com.androidplot.xy.XYPlot
import com.androidplot.xy.XYSeries
import kotlin.collections.toFloatArray
import kotlin.collections.toIntArray
import com.androidplot.xy.XYSeriesFormatter
import kotlinx.android.synthetic.main.temperature_activity.*
import kotlin.collections.ArrayList
class TemperatureActivity: AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.temperature_activity)
        val temp_ricevuta = intent.getStringArrayListExtra("Temperatura")
        //val temp_ricevuta = intent.getFloatArrayExtra("Chiave")
        val time_ricevuto = intent.getStringArrayListExtra("TempoTemperatura")
        val tempo = arrayListOf(time_ricevuto)
        println(tempo)
        val intArray = temp_ricevuta?.map { it.toDouble() }
        println("xxxxxx")
        //println(intArray)




        //println(time_ricevuto)
        //println(temp_ricevuta)

        val size = intArray!!.size
        //val domainLabels = arrayOf<Number>(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23);
        var series1Number: Array<Double> = Array(size){0.0}
        //var series1Number = arrayOf<Double>(0.0,0.0,0.0)
        //val array: Array<Double> = Array(size) { 0.0 }
            for (i in intArray!!.indices) {
                series1Number[i] = intArray[i]
            }

        // val series1Number = arrayOf<Number>(7,7,6,6,5,5,4,5,5,6,8,10,11,13,14,14,15,14,14,12,11,10,8,8);
        // val series2Number = arrayOf<Number>(2,8,4,7,32,16,64,12,7,10);


        val series1 : XYSeries = SimpleXYSeries(Arrays.asList(* series1Number),SimpleXYSeries.ArrayFormat.Y_VALS_ONLY
            ,"Temperature")
        // val series2 : XYSeries = SimpleXYSeries(Arrays.asList(* series2Number),SimpleXYSeries.ArrayFormat.Y_VALS_ONLY
        //     ,"Series 1");

        val series1Format = LineAndPointFormatter(Color.BLUE,Color.BLACK,null,null)
        //val series2Format = LineAndPointFormatter(Color.DKGRAY,Color.LTGRAY,null,null)

        series1Format.setInterpolationParams(CatmullRomInterpolator.Params(24,
            CatmullRomInterpolator.Type.Centripetal))
        //series2Format.setInterpolationParams(CatmullRomInterpolator.Params(24,
        //    CatmullRomInterpolator.Type.Centripetal))

        plot.addSeries(series1,series1Format)
        plot.setRangeBoundaries(15, 40, BoundaryMode.FIXED)
        //plot.addSeries(series2,series2Format)

        plot.graph.getLineLabelStyle(XYGraphWidget.Edge.BOTTOM).format = object : Format() {
            override fun format(
                obj: Any?,
                toAppendTo: StringBuffer,
                pos: FieldPosition
            ): StringBuffer {
                val i = Math.round((obj as Number).toFloat())
                return toAppendTo.append(time_ricevuto!![i])
            }

            override fun parseObject(source: String?, pos: ParsePosition): Any? {
                return null
            }

        }
        PanZoom.attach(plot)

        val btn_week = findViewById<Button>(R.id.button_week)
        //Faccio partire le varie activity
        btn_week.setOnClickListener {
            val intent = Intent(this, TempWeekActivity::class.java)
            startActivity(intent)
        }
        val btn_month = findViewById<Button>(R.id.button_month)
        //Faccio partire le varie activity
        btn_month.setOnClickListener {
            val intent = Intent(this, TempMonthActivity::class.java)
            startActivity(intent)
        }

    }
}
package org.andre

import org.apache.spark.sql.SparkSession

object HelloFelidae {
  def main(args: Array[String]) {
    val spark = SparkSession.builder().appName("HelloFelidae").getOrCreate()
    import spark.implicits._
    val name = if (args.length > 0) args(0) else ""
    println(s"Felidae Family: name=$name")
    val df = Seq( 
      (100, "jaguar peruviana"), 
      (101, "jaguar centralis"), 
      (102, "jaguar palustris"), 
      (200, "Sumatran tiger"),
      (201, "Amur tiger"),
      (202, "Bengal tiger"),
      (300, "Lion"),
      (400, "Snow Leopard")).toDF("id", "name") 
    df.filter(s"name like '%${name}%'").show(100,false)
    println("Now: "+new java.util.Date())
  }
}

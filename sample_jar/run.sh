
# toggle
jar=target/scala-2.11/amm-hellofelidae_2.11-0.1-SNAPSHOT.jar
jar=target/amm-HelloFelidae-1.0-SNAPSHOT.jar

spark-submit --class org.andre.HelloFelidae --master local[2] $jar $*


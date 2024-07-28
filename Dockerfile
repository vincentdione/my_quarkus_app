# Use the official JDK 19 image as the base image for the build stage
FROM openjdk:17-jdk AS build

# Enable preview features
ENV JAVA_OPTS="--enable-preview"

# Set the working directory
WORKDIR /app

#RUN mvn clean verify sonar:sonar \
#  -Dsonar.projectKey=my_quarkus_app \
#  -Dsonar.host.url=http://sonarqube:9000 \
#  -Dsonar.login=your-sonar-token

# Copy the Maven wrapper
COPY mvnw ./

COPY .mvn .mvn/

# Copy the pom.xml file
COPY pom.xml ./
COPY sonar.properties ./

# Download dependencies and cache them
RUN ./mvnw dependency:go-offline -B

# Copy the source code
COPY ./src ./src

# Compile and package the application
RUN ./mvnw package -Dmaven.test.skip=true -Dmaven.javadoc.skip=true -B -V


# Use the official JDK 19 image as the base image for the runtime stage
FROM openjdk:17-jdk AS runtime

# Enable preview features
ENV JAVA_OPTS="-Dquarkus.http.host=0.0.0.0 -Djava.util.logging.manager=org.jboss.logmanager.LogManager --enable-preview"

# Set the working directory
WORKDIR /app

# Copy the build artifacts from the build stage
#COPY --from=build /app/target/quarkus-app/quarkus-run.jar /app/app.jar
COPY --from=build /app/target/quarkus-app/lib/ /app/lib/
COPY --from=build /app/target/quarkus-app/*.jar /app/
COPY --from=build /app/target/quarkus-app/app/ /app/app/
COPY --from=build /app/target/quarkus-app/quarkus/ /app/quarkus/

# Set the entrypoint and command to run the application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/quarkus-run.jar"]




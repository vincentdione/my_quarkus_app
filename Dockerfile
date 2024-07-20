# Stage 1: Build the application
FROM maven:3.8.5-openjdk-17 AS build

# Define build arguments
ARG QUARKUS_PROFILE

# Set the working directory inside the container
WORKDIR /workspace

# Copy the Maven project files
COPY pom.xml ./
COPY src ./src

RUN echo $QUARKUS_PROFILE

# Package the application using Maven
RUN mvn clean package -Dquarkus.profile=${QUARKUS_PROFILE} -DskipTests

# Stage 2: Create the runtime image
FROM registry.access.redhat.com/ubi8/openjdk-17:1.14 AS runtime

# Define arguments for the runtime
ARG QUARKUS_PROFILE
ARG APP_NAME

# Set environment variables
ENV JAVA_OPTIONS="-Dquarkus.profile=${QUARKUS_PROFILE}"

# Set the working directory
WORKDIR /app

# Copy the application from the build stage
COPY --from=build /workspace/target/quarkus-app ./

# Expose the application port
EXPOSE 8080

# Command to run the application
CMD ["java", "-jar", "quarkus-run.jar", ${JAVA_OPTIONS}]

# Stage 1: Build the application
FROM maven:3.8.5-openjdk-17 AS build

# Define build arguments
ARG QUARKUS_PROFILE
ARG APP_NAME
# Set the working directory inside the container
WORKDIR /workspace


# Display the working directory and its contents
RUN echo "Working directory:" && ls -la && pwd

# Display the build arguments
RUN echo "QUARKUS_PROFILE is set to: $QUARKUS_PROFILE"
RUN echo "APP_NAME is set to: $APP_NAME"

# Makefile for hosts-manager Docker image

# Registry for storing the built image
RELEASE_REGISTRY ?= your-harbor-registry.example.com

# Version tag for the image, defaults to current date (YYYY-MM-DD)
VERSION ?= $(shell date +%Y-%m-%d)

# Image name
IMAGE_NAME = hosts-manager
FULL_IMAGE_NAME = $(RELEASE_REGISTRY)/$(IMAGE_NAME):$(VERSION)

# Default target
.PHONY: all
all: build

# Build the Docker image
.PHONY: build
build:
	@echo "Building Docker image: $(FULL_IMAGE_NAME)"
	docker build -t $(FULL_IMAGE_NAME) .
	@echo "Image built successfully"

# Push the Docker image to the registry
.PHONY: push
push: build
	@echo "Pushing image to registry: $(FULL_IMAGE_NAME)"
	docker push $(FULL_IMAGE_NAME)
	@echo "Image pushed successfully"

# Build and push in one command
.PHONY: release
release: push

# Run the container locally
.PHONY: run
run: build
	docker-compose up -d

# Stop the local container
.PHONY: stop
stop:
	docker-compose down

# Show help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build    - Build the Docker image"
	@echo "  push     - Build and push the image to registry"
	@echo "  release  - Alias for push"
	@echo "  run      - Run the container locally using docker-compose"
	@echo "  stop     - Stop the local container"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  RELEASE_REGISTRY - Registry for storing the image (default: your-harbor-registry.example.com)"
	@echo "  VERSION          - Image tag (default: current date in YYYY-MM-DD format)"

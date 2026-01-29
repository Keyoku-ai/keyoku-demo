"""Predefined state schemas for the Stateful AI demo."""

# Order Processing Schema - tracks order workflow state
ORDER_PROCESSING_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"],
            "description": "Current order status in the fulfillment pipeline"
        },
        "items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of items in the order"
        },
        "total_amount": {
            "type": "number",
            "minimum": 0,
            "description": "Total order amount in USD"
        },
        "customer_name": {
            "type": "string",
            "description": "Name of the customer"
        },
        "shipping_address": {
            "type": "string",
            "description": "Delivery address for the order"
        },
        "payment_method": {
            "type": "string",
            "enum": ["card", "paypal", "bank_transfer"],
            "description": "Selected payment method"
        },
        "notes": {
            "type": "string",
            "description": "Special instructions or notes"
        }
    }
}

ORDER_TRANSITION_RULES = {
    "status": {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["processing", "cancelled"],
        "processing": ["shipped", "cancelled"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": []
    }
}

# Support Ticket Schema - tracks customer support state
SUPPORT_TICKET_SCHEMA = {
    "type": "object",
    "properties": {
        "ticket_status": {
            "type": "string",
            "enum": ["open", "in_progress", "waiting_customer", "resolved", "closed"],
            "description": "Current ticket status"
        },
        "priority": {
            "type": "string",
            "enum": ["low", "medium", "high", "urgent"],
            "description": "Ticket priority level"
        },
        "category": {
            "type": "string",
            "enum": ["billing", "technical", "shipping", "returns", "general"],
            "description": "Issue category"
        },
        "issue_summary": {
            "type": "string",
            "description": "Brief summary of the issue"
        },
        "resolution_notes": {
            "type": "string",
            "description": "Notes about how the issue was resolved"
        },
        "customer_satisfaction": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "Customer satisfaction rating (1-5)"
        }
    }
}

SUPPORT_TRANSITION_RULES = {
    "ticket_status": {
        "open": ["in_progress", "closed"],
        "in_progress": ["waiting_customer", "resolved", "closed"],
        "waiting_customer": ["in_progress", "resolved", "closed"],
        "resolved": ["closed", "in_progress"],
        "closed": []
    }
}

# Appointment Scheduling Schema - tracks scheduling state
SCHEDULING_SCHEMA = {
    "type": "object",
    "properties": {
        "appointment_status": {
            "type": "string",
            "enum": ["proposed", "confirmed", "rescheduled", "cancelled", "completed"],
            "description": "Current appointment status"
        },
        "appointment_type": {
            "type": "string",
            "enum": ["consultation", "follow_up", "demo", "support"],
            "description": "Type of appointment"
        },
        "proposed_date": {
            "type": "string",
            "description": "Proposed date and time for the appointment"
        },
        "confirmed_date": {
            "type": "string",
            "description": "Confirmed date and time"
        },
        "duration_minutes": {
            "type": "integer",
            "minimum": 15,
            "maximum": 120,
            "description": "Duration in minutes"
        },
        "attendees": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of attendees"
        },
        "meeting_link": {
            "type": "string",
            "description": "Video meeting link if applicable"
        }
    }
}

SCHEDULING_TRANSITION_RULES = {
    "appointment_status": {
        "proposed": ["confirmed", "cancelled"],
        "confirmed": ["rescheduled", "cancelled", "completed"],
        "rescheduled": ["confirmed", "cancelled"],
        "cancelled": [],
        "completed": []
    }
}

# Demo agent configurations
DEMO_AGENTS = {
    "sales-agent": {
        "name": "Sales Agent",
        "description": "Handles order processing and sales inquiries",
        "schema_name": "OrderProcessing",
        "schema_definition": ORDER_PROCESSING_SCHEMA,
        "transition_rules": ORDER_TRANSITION_RULES,
        "system_prompt": """You are a friendly and helpful sales agent. Your job is to:
- Help customers place orders
- Recommend products based on their needs
- Process order confirmations
- Provide order status updates

Always be professional and helpful. When a customer wants to order something,
acknowledge their request and move the order through the appropriate states.
When you discuss order details (items, prices, addresses), the system will
automatically track these in the state."""
    },
    "support-agent": {
        "name": "Support Agent",
        "description": "Handles customer support tickets and issues",
        "schema_name": "SupportTicket",
        "schema_definition": SUPPORT_TICKET_SCHEMA,
        "transition_rules": SUPPORT_TRANSITION_RULES,
        "system_prompt": """You are a knowledgeable customer support agent. Your job is to:
- Help customers resolve issues
- Categorize and prioritize support requests
- Provide clear solutions and workarounds
- Escalate when necessary

Be empathetic and solution-focused. When handling issues, identify the category,
assess priority, and work toward resolution. The system tracks ticket status
automatically based on your conversation."""
    },
    "scheduler-agent": {
        "name": "Scheduler Agent",
        "description": "Handles appointment scheduling and calendar management",
        "schema_name": "AppointmentScheduling",
        "schema_definition": SCHEDULING_SCHEMA,
        "transition_rules": SCHEDULING_TRANSITION_RULES,
        "system_prompt": """You are an efficient scheduling assistant. Your job is to:
- Help schedule appointments and meetings
- Propose available time slots
- Confirm or reschedule appointments
- Send meeting reminders and details

Be organized and clear about scheduling details. When discussing appointments,
mention specific dates, times, and participants. The system automatically tracks
appointment status based on your conversation."""
    }
}

# Demo scenarios for guided testing
DEMO_SCENARIOS = {
    "none": {
        "name": "(Default) Free Chat",
        "description": "Free chat mode - type anything to start extracting state",
        "agent": "sales-agent",
        "sample_messages": []
    },
    "order_flow": {
        "name": "Order Processing Flow",
        "description": "Track an order from placement to delivery",
        "agent": "sales-agent",
        "sample_messages": [
            "Hi, I'd like to order a laptop and a wireless mouse",
            "Yes, ship it to 123 Main Street, San Francisco, CA 94105",
            "I'll pay with my credit card",
            "Please confirm the order",
            "What's the status of my order?"
        ]
    },
    "support_ticket": {
        "name": "Support Ticket Resolution",
        "description": "Handle a customer support issue end-to-end",
        "agent": "support-agent",
        "sample_messages": [
            "I have a problem with my recent order - it arrived damaged",
            "The laptop screen has a crack on the corner",
            "I'd like a replacement please",
            "Thank you for your help!"
        ]
    },
    "multi_agent": {
        "name": "Multi-Agent Collaboration",
        "description": "Show state sharing between different agents",
        "agents": ["sales-agent", "support-agent", "scheduler-agent"],
        "sample_flow": [
            {"agent": "sales-agent", "message": "I want to order a laptop for $1200"},
            {"agent": "support-agent", "message": "I have a question about the laptop warranty"},
            {"agent": "scheduler-agent", "message": "Schedule a product demo for next Tuesday at 2pm"}
        ]
    }
}

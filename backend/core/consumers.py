from channels.generic.websocket import AsyncWebsocketConsumer
import json

class SnapshotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.current_group = None  # Track current group subscription
        await self.accept()

    async def disconnect(self, close_code):
        if self.current_group:
            await self.channel_layer.group_discard(
                self.current_group,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "subscribe":
            machine_id = data.get("machine_id")
            new_group = f"machine_{machine_id}"

            # Leave previous group if any
            if self.current_group:
                await self.channel_layer.group_discard(
                    self.current_group,
                    self.channel_name
                )

            # Join new group
            await self.channel_layer.group_add(
                new_group,
                self.channel_name
            )
            self.current_group = new_group
            print(self.current_group)

            await self.send(text_data=json.dumps({
                "type": "subscribed",
                "message": {
                    "machine_id": machine_id
                }
            }))

    async def snapshot_message(self, event):
        """
        Handler to receive snapshot updates pushed from the backend.
        """
        await self.send(text_data=json.dumps(event))

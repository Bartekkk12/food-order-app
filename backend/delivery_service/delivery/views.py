from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Delivery
from .serializers import *


class HealthCheckView(APIView):
    """Health check endpoint for Docker"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({'status': 'healthy'}, status=status.HTTP_200_OK)


class DeliveryListView(generics.ListAPIView):
    """List all deliveries"""
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [AllowAny]


class DeliveryDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a delivery"""
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [AllowAny]


class DeliveryByOrderView(APIView):
    """Get delivery by order_id"""
    permission_classes = [AllowAny]
    
    def get(self, request, order_id):
        try:
            delivery = Delivery.objects.get(order_id=order_id)
            serializer = DeliverySerializer(delivery)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Delivery.DoesNotExist:
            return Response(
                {'error': f'Delivery for order {order_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateDeliveryStatusView(APIView):
    """Update delivery status"""
    permission_classes = [AllowAny]
    
    def patch(self, request, pk):
        try:
            delivery = Delivery.objects.get(pk=pk)
        except Delivery.DoesNotExist:
            return Response(
                {'error': 'Delivery not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateDeliveryStatusSerializer(
            delivery,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                DeliverySerializer(delivery).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


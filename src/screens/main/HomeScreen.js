import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Button, Avatar } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { appointmentApi } from '../../api/appointments';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

export default function HomeScreen() {
  const [upcomingAppointments, setUpcomingAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const navigation = useNavigation();

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const data = await appointmentApi.getAppointments('upcoming');
      setUpcomingAppointments(data);
      setError(null);
    } catch (err) {
      setError('Failed to load appointments');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAppointments();
  }, []);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    loadAppointments().finally(() => setRefreshing(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {upcomingAppointments.map((appointment) => (
        <Card key={appointment.id} style={styles.card}>
          <Card.Content>
            <View style={styles.header}>
              <Avatar.Image
                size={50}
                source={{ uri: appointment.doctor.avatar_url }}
              />
              <View style={styles.doctorInfo}>
                <Title>{appointment.doctor.name}</Title>
                <Paragraph>{appointment.doctor.specialization}</Paragraph>
              </View>
            </View>
            <View style={styles.appointmentInfo}>
              <Paragraph>Date: {new Date(appointment.datetime).toLocaleDateString()}</Paragraph>
              <Paragraph>Time: {new Date(appointment.datetime).toLocaleTimeString()}</Paragraph>
              <Paragraph>Status: {appointment.status}</Paragraph>
            </View>
          </Card.Content>
          <Card.Actions>
            <Button onPress={() => navigation.navigate('AppointmentDetail', { id: appointment.id })}>
              View Details
            </Button>
          </Card.Actions>
        </Card>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 10,
  },
  card: {
    marginBottom: 10,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  doctorInfo: {
    marginLeft: 10,
  },
  appointmentInfo: {
    marginTop: 10,
  },
}); 
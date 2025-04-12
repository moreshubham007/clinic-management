import React, { useState, useEffect } from 'react';
import { ScrollView, RefreshControl, StyleSheet } from 'react-native';
import { Card, Avatar, Title, Paragraph } from 'react-native-paper';
import { appointmentApi } from '../../src/api/appointments';
import { LoadingSpinner } from '../../src/components/LoadingSpinner';
import { ErrorMessage } from '../../src/components/ErrorMessage';

export default function HomeScreen() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      const data = await appointmentApi.getAppointments();
      setAppointments(data);
      setError(null);
    } catch (err) {
      setError('Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAppointments();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAppointments();
    setRefreshing(false);
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {appointments.map((appointment) => (
        <Card key={appointment.id} style={styles.card}>
          <Card.Title
            title={appointment.doctor.name}
            subtitle={appointment.doctor.specialization}
            left={(props) => (
              <Avatar.Image
                {...props}
                source={{ uri: appointment.doctor.avatar_url }}
              />
            )}
          />
          <Card.Content>
            <Title>{new Date(appointment.datetime).toLocaleDateString()}</Title>
            <Paragraph>Time: {new Date(appointment.datetime).toLocaleTimeString()}</Paragraph>
            <Paragraph>Status: {appointment.status}</Paragraph>
            {appointment.symptoms && (
              <Paragraph>Symptoms: {appointment.symptoms}</Paragraph>
            )}
          </Card.Content>
        </Card>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  card: {
    margin: 8,
    elevation: 4
  }
}); 
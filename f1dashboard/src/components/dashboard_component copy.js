import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE_URL } from '../api'
import { getTelemetry } from '../api'
import {
  Select,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Box,
  Flex,
  Text,
  VStack,
  useToast,
  IconButton,
  Tooltip,
} from '@chakra-ui/react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts'
import { ChevronDown, Activity, Gauge, Zap, Disc, RotateCw, Wind, ChevronLeft, ChevronRight } from 'lucide-react'

export default function DashboardComponent() {
  const [year, setYear] = useState(new Date().getFullYear())
  const [gp, setGp] = useState('')
  const [session, setSession] = useState('R')
  const [driver1, setDriver1] = useState('VER')
  const [driver2, setDriver2] = useState('HAM')
  const [lap, setLap] = useState(1)
  const [maxLaps, setMaxLaps] = useState(50)
  const [telemetryData, setTelemetryData] = useState([])
  const [gpOptions, setGpOptions] = useState([])
  const [driverOptions, setDriverOptions] = useState([])
  const toast = useToast()

  // Fetch GP options
  useEffect(() => {
    const fetchGrandPrixOptions = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}grand_prix_options/`, { params: { year } })
        setGpOptions(response.data)
        if (response.data.length > 0) {
          setGp(response.data[0].id.toString())
        }
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to fetch Grand Prix options',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    }

    fetchGrandPrixOptions()
  }, [year, toast])

  // Fetch Driver options
  useEffect(() => {
    const fetchDriverOptions = async () => {
      if (!year || !gp || !session) return

      try {
        const response = await axios.get(`${API_BASE_URL}driver_options/`, {
          params: { year, grand_prix_id: gp, session },
        })
        setDriverOptions(response.data)
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to fetch driver options',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    }

    fetchDriverOptions()
  }, [year, gp, session, toast])

  // Fetch Telemetry Data
  useEffect(() => {
    const fetchData = async () => {
      if (!year || !gp || !session || !driver1 || !driver2 || !lap) return

      try {
        const params = {
          year,
          grand_prix_id: gp,
          session,
          driver: [driver1, driver2],
          lap,
        }

        const response = await getTelemetry(params)
        const data = response.data

        const processedData = processTelemetryData(data)
        setTelemetryData(processedData)
        setMaxLaps(Math.max(...processedData.map(d => d.lap)))
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to fetch telemetry data',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    }

    fetchData()
  }, [year, gp, session, driver1, driver2, lap, toast])

  const processTelemetryData = (data) => {
    return data.map(d => ({
      distance: d.distance,
      lap: d.lap,
      [d.driver]: d,
    }))
  }

  const renderChart = (dataKey, yAxisLabel, Icon) => (
    <Card bg="white" shadow="lg" borderRadius="xl">
      <CardHeader>
        <Flex align="center" justify="space-between">
          <Heading size="md" fontWeight="bold">{yAxisLabel}</Heading>
          <Icon size={20} />
        </Flex>
      </CardHeader>
      <CardBody>
        <Box height="250px">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={telemetryData.filter(d => d.lap === lap)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="distance" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Line type="monotone" dataKey={`${driver1}.${dataKey}`} stroke="#3182CE" strokeWidth={2} name={driver1} />
              <Line type="monotone" dataKey={`${driver2}.${dataKey}`} stroke="#E53E3E" strokeWidth={2} name={driver2} />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </CardBody>
    </Card>
  )

  return (
    <Box minH="100vh" bg="gray.50">
      <Box as="header" bg="white" shadow="lg" p={4}>
        <Flex maxW="container.xl" mx="auto" align="center" justify="space-between">
          <Flex align="center">
            <Activity size={28} color="#3182CE" />
            <Text fontWeight="bold" fontSize="xl" ml={2}>F1 Telemetry Dashboard</Text>
          </Flex>
          <Flex align="center">
            <Select value={year.toString()} onChange={(e) => setYear(parseInt(e.target.value))} mr={2} bg="white" borderColor="gray.300">
              {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map((y) => (
                <option key={y} value={y.toString()}>{y}</option>
              ))}
            </Select>
            <Select value={gp} onChange={(e) => setGp(e.target.value)} mr={2} width="auto" icon={<ChevronDown />} bg="white" borderColor="gray.300">
              {gpOptions.map((option, index) => (
                <option key={option.id || index} value={option.id ? option.id.toString() : ''}>
                  {option.name || 'Unknown GP'}
                </option>
              ))}
            </Select>
            <Select value={session} onChange={(e) => setSession(e.target.value)} bg="white" borderColor="gray.300">
              <option value="FP1">FP1</option>
              <option value="FP2">FP2</option>
              <option value="FP3">FP3</option>
              <option value="Q">Qualifying</option>
              <option value="R">Race</option>
            </Select>
          </Flex>
        </Flex>
      </Box>

      <Box as="main" maxW="container.xl" mx="auto" py={6}>
        <VStack spacing={6}>
          <Flex width="full" justify="space-between" wrap="wrap">
            <Card width={{ base: 'full', md: '48%' }} bg="white" shadow="lg" borderRadius="xl">
              <CardHeader>
                <Flex align="center" justify="space-between">
                  <Heading size="md" fontWeight="bold">Driver 1</Heading>
                </Flex>
              </CardHeader>
              <CardBody>
                <Select value={driver1} onChange={(e) => setDriver1(e.target.value)} icon={<ChevronDown />} bg="white" borderColor="gray.300">
                  {driverOptions.map((option, index) => (
                    <option key={option.id || index} value={option.id ? option.id.toString() : ''}>
                      {option.name || 'Unknown Driver'}
                    </option>
                  ))}
                </Select>
              </CardBody>
            </Card>

            <Card width={{ base: 'full', md: '48%' }} bg="white" shadow="lg" borderRadius="xl">
              <CardHeader>
                <Flex align="center" justify="space-between">
                  <Heading size="md" fontWeight="bold">Driver 2</Heading>
                </Flex>
              </CardHeader>
              <CardBody>
                <Select value={driver2} onChange={(e) => setDriver2(e.target.value)} icon={<ChevronDown />} bg="white" borderColor="gray.300">
                  {driverOptions.map((option, index) => (
                    <option key={option.id || index} value={option.id ? option.id.toString() : ''}>
                      {option.name || 'Unknown Driver'}
                    </option>
                  ))}
                </Select>
              </CardBody>
            </Card>
          </Flex>

          <Card bg="white" shadow="lg" borderRadius="xl" width="full">
            <CardHeader>
              <Flex align="center" justify="space-between">
                <Heading size="md" fontWeight="bold">Lap Selection</Heading>
              </Flex>
            </CardHeader>
            <CardBody>
              <Flex align="center" justify="space-between" width="100%">
                <Tooltip label="Previous Lap">
                  <IconButton
                    icon={<ChevronLeft />}
                    onClick={() => setLap(prev => Math.max(1, prev - 1))}
                    isDisabled={lap === 1}
                    aria-label="Previous Lap"
                  />
                </Tooltip>
                <Box width="calc(100% - 100px)" px={4}>
                  <Slider
                    aria-label="lap-slider"
                    value={lap}
                    min={1}
                    max={maxLaps}
                    step={1}
                    onChange={(val) => setLap(val)}
                  >
                    <SliderTrack bg="blue.100" height="10px" borderRadius="full">
                      <SliderFilledTrack bg="blue.500" />
                    </SliderTrack>
                    <SliderThumb boxSize={6} />
                  </Slider>
                </Box>
                <Tooltip label="Next Lap">
                  <IconButton
                    icon={<ChevronRight />}
                    onClick={() => setLap(prev => Math.min(maxLaps, prev + 1))}
                    isDisabled={lap === maxLaps}
                    aria-label="Next Lap"
                  />
                </Tooltip>
              </Flex>
              <Text textAlign="center" mt={4} fontWeight="bold">Lap: {lap} / {maxLaps}</Text>
            </CardBody>
          </Card>

          <Tabs isFitted variant="enclosed-colored" colorScheme="blue" width="full">
            <TabList mb="1em">
              <Tab>Speed</Tab>
              <Tab>Throttle</Tab>
              <Tab>Brake</Tab>
              <Tab>Gear</Tab>
              <Tab>RPM</Tab>
              <Tab>DRS</Tab>
            </TabList>

            <TabPanels>
              <TabPanel>{renderChart('speed', 'Speed (km/h)', Gauge)}</TabPanel>
              <TabPanel>{renderChart('throttle', 'Throttle (%)', Zap)}</TabPanel>
              <TabPanel>{renderChart('brake', 'Brake (%)', Disc)}</TabPanel>
              <TabPanel>{renderChart('gear', 'Gear', RotateCw)}</TabPanel>
              <TabPanel>{renderChart('rpm', 'RPM', Activity)}</TabPanel>
              <TabPanel>{renderChart('drs', 'DRS', Wind)}</TabPanel>
            </TabPanels>
          </Tabs>
        </VStack>
      </Box>
    </Box>
  )
}

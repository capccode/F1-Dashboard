import { useState, useEffect } from 'react'
import axios from 'axios'
import qs from 'qs'
import { API_BASE_URL } from '../api'
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
  ChakraProvider,
  extendTheme,
} from '@chakra-ui/react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts'
import { ChevronDown, Activity, Gauge, Zap, Disc, RotateCw, Wind, ChevronLeft, ChevronRight } from 'lucide-react'

const theme = extendTheme({
  colors: {
    brand: {
      50: '#E5F0FF',
      100: '#B8D5FF',
      500: '#0052CC',
      600: '#0047B3',
    },
    accent: {
      500: '#FF3B30',
    },
  },
  components: {
    Card: {
      baseStyle: {
        container: {
          borderRadius: 'lg',
          boxShadow: 'lg',
        },
      },
    },
    Heading: {
      baseStyle: {
        fontWeight: 'bold',
      },
    },
    Tabs: {
      variants: {
        'enclosed-colored': {
          tab: {
            _selected: {
              color: 'brand.500',
              bg: 'brand.50',
            },
          },
        },
      },
    },
  },
})

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

  useEffect(() => {
    const fetchData = async () => {
      if (!year || !gp || !session || !driver1 || !driver2 || !lap) return

      try {
        const params = {
          year,
          grand_prix_id: gp,
          session,
          driver: [driver1, driver2],  // Send the driver as a list without []
          lap,
        }

        const response = await axios.get(`${API_BASE_URL}telemetry_data/`, {
          params: params,
          paramsSerializer: (params) => {
            return qs.stringify(params, { arrayFormat: 'repeat' });  // ensures correct serialization
          }
        })
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
    <Card>
      <CardHeader>
        <Flex align="center" justify="space-between">
          <Heading size="md">{yAxisLabel}</Heading>
          <Icon size={20} color={theme.colors.brand[500]} />
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
              <Line type="monotone" dataKey={`${driver1}.${dataKey}`} stroke={theme.colors.brand[500]} strokeWidth={2} name={driver1} />
              <Line type="monotone" dataKey={`${driver2}.${dataKey}`} stroke={theme.colors.accent[500]} strokeWidth={2} name={driver2} />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </CardBody>
    </Card>
  )

  return (
    <ChakraProvider theme={theme}>
      <Box minH="100vh" bg="gray.50">
        <Box as="header" bg="white" shadow="md" p={4}>
          <Flex maxW="container.xl" mx="auto" align="center" justify="space-between">
            <Flex align="center">
              <Activity size={28} color={theme.colors.brand[500]} />
              <Text fontWeight="bold" fontSize="2xl" ml={2} color="brand.500">F1 Telemetry Dashboard</Text>
            </Flex>
            <Flex align="center" gap={2}>
              <Select value={year.toString()} onChange={(e) => setYear(parseInt(e.target.value))} bg="white" borderColor="gray.300">
                {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map((y) => (
                  <option key={y} value={y.toString()}>{y}</option>
                ))}
              </Select>
              <Select value={gp} onChange={(e) => setGp(e.target.value)} width="auto" icon={<ChevronDown />} bg="white" borderColor="gray.300">
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
            <Flex width="full" justify="space-between" wrap="wrap" gap={4}>
              <Card width={{ base: 'full', md: '48%' }}>
                <CardHeader>
                  <Heading size="md">Driver 1</Heading>
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

              <Card width={{ base: 'full', md: '48%' }}>
                <CardHeader>
                  <Heading size="md">Driver 2</Heading>
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

            <Card width="full">
              <CardHeader>
                <Heading size="md">Lap Selection</Heading>
              </CardHeader>
              <CardBody>
                <Flex align="center" justify="space-between" width="100%">
                  <Tooltip label="Previous Lap">
                    <IconButton
                      icon={<ChevronLeft />}
                      onClick={() => setLap(prev => Math.max(1, prev - 1))}
                      isDisabled={lap === 1}
                      aria-label="Previous Lap"
                      colorScheme="brand"
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
                      colorScheme="brand"
                    >
                      <SliderTrack>
                        <SliderFilledTrack />
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
                      colorScheme="brand"
                    />
                  </Tooltip>
                </Flex>
                <Text textAlign="center" mt={4} fontWeight="bold">Lap: {lap} / {maxLaps}</Text>
              </CardBody>
            </Card>

            <Tabs isFitted variant="enclosed-colored" colorScheme="brand" width="full">
              <TabList mb="1em">
                <Tab>Speed</Tab>
                <Tab>Throttle</Tab>
                <Tab>Brake</Tab>
                <Tab>Gear</Tab>
                <Tab>RPM</Tab>
                <Tab>DRS</Tab>
              </TabList>

              <TabPanels>
                <TabPanel p={0}>{renderChart('speed', 'Speed (km/h)', Gauge)}</TabPanel>
                <TabPanel p={0}>{renderChart('throttle', 'Throttle (%)', Zap)}</TabPanel>
                <TabPanel p={0}>{renderChart('brake', 'Brake (%)', Disc)}</TabPanel>
                <TabPanel p={0}>{renderChart('gear', 'Gear', RotateCw)}</TabPanel>
                <TabPanel p={0}>{renderChart('rpm', 'RPM', Activity)}</TabPanel>
                <TabPanel p={0}>{renderChart('drs', 'DRS', Wind)}</TabPanel>
              </TabPanels>
            </Tabs>
          </VStack>
        </Box>
      </Box>
    </ChakraProvider>
  )
}

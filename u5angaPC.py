# (c) 2019 Anirban Banerjee
#from u5anga import *; u = u5anga(5.5, 12.93340, 77.59630)
#Licensed under:
#GNU GENERAL PUBLIC LICENSE
#Version 3, 29 June 2007
import math

class u5angaPC ():
	monthList = ["January","February","March","April","May","June",
	   "July","August","September","October","November","December"]

	rashiList = ["Mesha","Vrisha","Mithuna","Karka","Simha","Kanya","Tula",
	   "Vrischika","Dhanu","Makara","Kumbha","Meena"]

	dayList = ["Sun","Mon","Tues","Wednes","Thurs","Fri","Satur"]
	vaaraList = ["Ravi","Soma","Mangal","Budh","Brihaspati","Shukra","Shani"]

	tithiList = ["Pratipad","Dvitiya","Tritiya","Chaturthi","Panchami",
			"Shashthi","Saptami","Ashtami","Navami","Dashami","Ekadashi",
			"Dvadashi","Trayodashi","Chaturdashi","Purnima","Pratipad",
			"Dvitiya","Tritiya","Chaturthi","Panchami","Shashthi",
			"Saptami","Ashtami","Navami","Dashami","Ekadashi","Dvadashi",
			"Trayodashi","Chaturdashi","Amaavasya"]

	karanaList = ["Bava","Baalava","Kaulava","Taitula","Garija","Vanija",
	   "Vishti","Shakuni","Chatushpada","Naga","Kimstughna"]

	yogaList = ["Vishakumbha","Preeti","Ayushman","Saubhagya","Shobhana",
	   "Atiganda","Sukarman","Dhriti","Shula","Ganda","Vriddhi",
	   "Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
	   "Variyan","Parigha","Shiva","Siddha","Saadhya","Shubha","Shukla",
	   "Brahma","Indra","Vaidhriti"]

	nakshatraList = ["Ashvini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
			"Punarvasu","Pushya","Ashlesa","Magha","Purva Phalguni","Uttara Phalguni",
			"Hasta","Chitra","Svaati","Vishakha","Anuradha","Jyeshtha","Mula",
			"Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
			"Purva Bhaadra","Uttara Bhaadra","Revati"]

	def __init__ (self, zhr=5.5, latt=12.9716, longt=77.5946):
		self.latitude = float(latt)
		self.longitude = float(longt)
		self.zoneHour = float(zhr)

	def setzone (self, zhr=5.5, latt=12.9716, longt=77.5946):
		self.latitude = float(latt)
		self.longitude = float(longt)
		self.zoneHour = float(zhr)

	def ts_at_mn (self, dd, mm, yyyy):
		#timescale at midnight
		#https://stjarnhimlen.se/comp/ppcomp.html#3
		#The time scale in these formulae are counted in days. 
		#Hours, minutes, seconds are expressed as fractions of a day. 
		#Day 0.0 occurs at 2000 Jan 0.0 UT (or 1999 Dec 31, 24:00 UT). 
		#This "day number" d is computed as follows (y=year, m=month, D=date, 
		#UT=UT in hours+decimals):

		#d = 367*yyyy \
		#	- 7 * ( yyyy + (mm+9)/12 ) / 4 \
		#	- 3 * ( ( yyyy + (mm-9)/7 ) / 100 + 1 ) / 4 \
		#	+ 275*mm/9 + dd - 730515

		d = int(dd)
		m = int(mm)
		y = int(yyyy)
		
		d = 367*y \
			- 7 * ( y + (m+9)//12 ) // 4 \
			- 3 * ( ( y + (m-9)//7 ) // 100 + 1 ) // 4 \
			+ 275*m//9 + d - 730515
		
		return d - (self.zoneHour)/24.0 #add 2451543.5 to get Julian Date

	def radians (self, degrees):
		return (3.1415926535897932 * degrees / 180.0)

	def degrees (self, radians):
		return (180.0 * radians /3.1415926535897932)

	def  sun_esrl (self, 
			julian_day, 
			zhr, 
			latt, 
			longt):

		julian_century = (julian_day - 2451545.0)/36525.0 #G
		sun_geom_mean_long_deg = (280.46646+julian_century*(36000.76983+julian_century*0.0003032)) % 360.0 #I
		sun_geom_mean_anom_deg = 357.52911+julian_century*(35999.05029-0.0001537*julian_century) #J
		earth_orbit_eccentricity = 0.016708634-julian_century*(0.000042037+0.0000001267*julian_century) #K
		sun_eqn_of_centre = math.sin(self.radians(sun_geom_mean_anom_deg))* \
							(1.914602-julian_century*(0.004817+0.000014*julian_century))+ \
							math.sin(self.radians(2*sun_geom_mean_anom_deg))* \
							(0.019993-0.000101*julian_century)+ \
							math.sin(self.radians(3*sun_geom_mean_anom_deg))*0.000289 #L
		sun_true_long_deg = sun_geom_mean_long_deg + sun_eqn_of_centre #M
		#sun_true_anom_deg = sun_geom_mean_anom_deg + sun_eqn_of_centre #N
		#sun_rad_vector_au = (1.000001018*(1-earth_orbit_eccentricity*earth_orbit_eccentricity))/ \
		#						(1+earth_orbit_eccentricity*math.cos(radians(sun_true_anom_deg))) #O
		sun_apparent_long_deg = sun_true_long_deg-0.00569-0.00478* \
							math.sin(self.radians(125.04-1934.136*julian_century)) #P
		mean_oblique_ecliptic_deg = 23+(26+((21.448-julian_century*(46.815+ \
							julian_century*(0.00059-julian_century*0.001813))))/60.0)/60.0 #Q
		oblique_correction_deg = mean_oblique_ecliptic_deg+ \
							0.00256*math.cos(self.radians(125.04-1934.136*julian_century)) #R
		sun_right_ascension_deg = self.degrees(math.atan2(math.cos(self.radians(oblique_correction_deg))*math.sin(self.radians(sun_apparent_long_deg)), \
									math.cos(self.radians(sun_apparent_long_deg)))) #S
		sun_declination_deg = self.degrees(math.asin(math.sin(self.radians(oblique_correction_deg))* \
							math.sin(self.radians(sun_apparent_long_deg)))) #T
		var_y = math.tan(self.radians(oblique_correction_deg/2))*math.tan(self.radians(oblique_correction_deg/2)) #U
		equation_of_time_min = 4*self.degrees(var_y*math.sin(2*self.radians(sun_geom_mean_long_deg))- \
							2*earth_orbit_eccentricity*math.sin(self.radians(sun_geom_mean_anom_deg))+ \
							4*earth_orbit_eccentricity*var_y*math.sin(self.radians(sun_geom_mean_anom_deg))* \
							math.cos(2*self.radians(sun_geom_mean_long_deg))- \
							0.5*var_y*var_y*math.sin(4*self.radians(sun_geom_mean_long_deg))- \
							1.25*earth_orbit_eccentricity*earth_orbit_eccentricity* \
							math.sin(2*self.radians(sun_geom_mean_anom_deg))) #V
		hour_angle_cosine = math.cos(self.radians(90.833))/(math.cos(self.radians(latt))* \
							math.cos(self.radians(sun_declination_deg)))-math.tan(self.radians(latt))* \
							math.tan(self.radians(sun_declination_deg))

		if (hour_angle_cosine > 1.0):
			#sun never rises
			return 0.0, 0.0, 0.0
		elif (hour_angle_cosine < -1.0):
			#sun never sets
			return 0.0, 0.0, 24.0

		hour_angle_sunrise_deg = self.degrees(math.acos(math.cos(self.radians(90.833))/(math.cos(self.radians(latt))* \
							math.cos(self.radians(sun_declination_deg)))-math.tan(self.radians(latt))* \
							math.tan(self.radians(sun_declination_deg)))) #W

		solar_noon_LST = (720.0-4*longt-equation_of_time_min+zhr*60)/1440.0 #X

		sunriseLST = (solar_noon_LST - (hour_angle_sunrise_deg*4)/1440.0) * 24 #Y

		sunsetLST = (solar_noon_LST + (hour_angle_sunrise_deg*4)/1440.0)*24 #Z

		sunlight_duration_hrs = hour_angle_sunrise_deg * 8 / 60 #AA

		return sunriseLST, sunsetLST, sunlight_duration_hrs

	def rev(self, x):
		return  x - math.floor(x/360.0)*360.0

	def ayanansha (self, d):
		t = (d+36523.5)/36525
		o = self.rev(259.183275-1934.142008333206*t+0.0020777778*t*t)
		l = self.rev(279.696678+36000.76892*t+0.0003025*t*t)
		ayan = 17.23*math.sin(self.radians(o))+1.27*math.sin(self.radians(l*2))-(5025.64+1.11*t)*t
		#Based on Lahiri
		ayan = (ayan-80861.27)/3600.0
		return ayan

	def ayan (self, dd, mm, yyyy, hr):
		d = self.ts_at_mn (dd, mm, yyyy) + (hr/24.0)
		return self.ayanansha (d)

	def nakshatra (self, dd, mm, yyyy, hr):
		d = self.ts_at_mn (dd, mm, yyyy) + (hr/24.0)
		mlon, slon = self.calculate_moon_sun_long(d)
		nakshindex = (self.rev(mlon + self.ayan(d))*6//80) % 27
		print ("nakshatra =", self.nakshatraList[nakshindex])
		return nakshindex
		
	def ts_at_hr (self, dd, mm, yyyy, hr):
		return self.ts_at_mn (dd, mm, yyyy) + (hr/24.0)

	def yoga (self, dd, mm, yyyy, hr):
		return self.yogaindex(self.ts_at_hr (dd, mm, yyyy) + (hr/24.0))

	def yogaindex (self, d):
		mlon, slon = self.calculate_moon_sun_long (d)
		#return index to yoga table
		yogaindex = (self.rev(mlon + slon + 2*self.ayanansha(d))*6 // 80) % 27
		print ("yoga=", self.yogaList[yogaindex])
		return yogaindex

	def karana (self, dd, mm, yyyy, hr):
		return self.karanaindex(self.ts_at_hr (dd, mm, yyyy) + (hr/24.0))

	def karanaindex (self, d):
		karindex = self.calculate_tithi_index (d, 6.0)
		if karindex == 0:
			karindex = 10
		if karindex >= 57:
			karindex -= 50
		if karindex > 0 and karindex < 57:
			karindex = (karindex-1) - (math.floor((karindex-1)/7)*7) #anirb use floor
		karindex = karindex % 11
		print ("karana=", self.karanaList[karindex])
		return karindex
	
	def mrashi (self, dd, mm, yyyy, hr):
		return self.mrashindex(self.ts_at_hr (dd, mm, yyyy) + (hr/24.0))

	def mrashindex (self, d):
		rashindex = (self.rev(self.calculate_moon_sun_long (d) + self.ayanansha(d)) // 30) % 12
		print ("rashi=", self.rashiList[rashindex])
		return rashindex
	
	def vaara (self, dd, mm, yyyy):
		d = self.ts_at_mn (dd, mm, yyyy)
		d += (self.zoneHour/24.0)
		vaarindex = int((d+5)%7)
		print ("vaara=", self.vaaraList[vaarindex])
		return vaarindex

	def dtithi (self, d, m, y):
		#find all tithi changes starting at midnight on this date
		oldtithi = ''
		retVal = ''
		s = ' at '
		for minutes in range(1440):
			timescale = self.ts_at_mn (d, m, y) + (minutes/1440)
			#print ("timescale is ", timescale)
			tithi = self.tithiList[self.tithi(timescale)]
			if tithi != oldtithi:
				newm = str(int(minutes%60))
				if len(newm) < 2:
					newm = "0"+newm
				retVal += ' '+tithi+s+str(int(minutes/60))+":"+newm
				s = ' starting '
				#jump minutes for quicker calculation
				minutes += 700
				oldtithi = tithi
				if True:
				#if minutes < 1439:
					retVal += '\n'
		return retVal

	def ltithi (self, startyr, startm=1, endm=12, howmany=1):
		startm -= 1
		#list all tithis in a month range
		if startm < 1:
			startm = 0
		if startm > 12:
			startm = 11
		if endm > 12:
			endm = 12
		if endm < 1:
			endm = 1
		daylist = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
		i = 0
		oldtithi = ''
		retVal = ''
		while True:
			for m in range(startm, endm):
				for d in range(daylist[m]):
					leapyr = (startyr % 4 == 0) and ((startyr % 100 != 0) or (startyr % 400 == 0))
					for minutes in range(1440):
						timescale = self.ts_at_mn (d+1, m+1, startyr) + (minutes/1440)
						tithi = self.tithiList[self.tithi(timescale)]
						if tithi != oldtithi:
							newm = str(int(minutes%60))
							if len(newm) < 2:
								newm = "0"+newm
							i += 1
							if i > howmany:
								retVal += str(d+1)+"-"+str(m+1)+"-"+str(startyr)+","+str(int(minutes/60))+":"+newm+","+tithi
								return retVal
							else:
								retVal += str(d+1)+"-"+str(m+1)+"-"+str(startyr)+","+str(int(minutes/60))+":"+newm+","+tithi+'\n'
							oldtithi = tithi
					if m == 1 and d == 27 and not leapyr:
						break
					elif m == 1 and d == 28 and leapyr:
						break
					elif m == 11 and d == 30:
						startyr += 1
						break

	def calculate_moon_sun_long(self, d):
		#https://www.stjarnhimlen.se/comp/tutorial.html#7
		#printf ("calculate_moon_sun_long d= %.8f\n", d)
	
		#------------------------------Sun
		#below are in radians
		w = self.radians(self.rev(282.9404 + 4.70935e-5 * d))		#Sun's longitude of perihelion
		Ms = self.radians(self.rev(356.0470 + 0.9856002585 * d))	#Sun's mean anomaly
		#floatingpoint oblecl = 23.4393 - 3.563e-7 * d		#obliquity of the ecliptic
	
		e = 0.016709 - 1.151e-9 * d		#eccentricity
	
		E = Ms + e * math.sin(Ms) * (1 + e * math.cos(Ms)) #eccentricity anomaly
	
		#Sun's mean longitude
		Ls = w + Ms
	
		#Sun's rectangular coordinates
		x = math.cos(E) - e
		y = math.sin(E) * math.sqrt(1 - e*e)
	
		#distance from Sun and true anomaly
		#floatingpoint r = math.sqrt(x*x + y*y)	#in Earth radii
		v = math.atan2( y, x )		#true anomaly
		slon = self.rev(self.degrees(v + w))
		#printf ("Sun's longitude = %.8f\n", slon)
	
		#------------------------------Moon
		#all below are in radians
		N = self.radians(self.rev(125.1228 - 0.0529538083 * d))   #Longt of ascending node
		i = 0.089804			#Inclination in degrees is 5.1454
		w = self.radians(self.rev(318.0634 + 0.1643573223 * d))		#Arg. of perigee
		Mm = self.radians(self.rev(115.3654 + 13.0649929509 * d))  #Mean eccentricity anomaly
	
		a = 60.2666 #Mean distance in Earth equatorial radii
		e = 0.054900 #Eccentricity
	
		#iterate for accurate eccentricity anomaly
		E = Mm + e * math.sin(Mm) * (1 + e * math.cos(Mm))
		iteration = 0
		while (True):
			eps	= (E - e * math.sin(E) - Mm) / (1 - e * math.cos(E))
			E = E - eps
			if iteration > 50 or abs(eps) < 1e-5:
				break
	
		#compute rectangular (x,y) coordinates in the plane of the lunar orbit
		x = a * (math.cos(E) - e)
		y = a * math.sqrt(1 - e*e) * math.sin(E)
	
		r = math.sqrt(x*x + y*y) #distance Earth radii
		v = math.atan2(y, x) #true anomaly
	
		xeclip = r * (math.cos(N) * math.cos(v+w) - math.sin(N) * math.sin(v+w) * math.cos(i))
		yeclip = r * (math.sin(N) * math.cos(v+w) + math.cos(N) * math.sin(v+w) * math.cos(i))
		#floatingpoint zeclip = r * math.sin(v+w) * math.sin(i)
	
		mlon =  self.rev(self.degrees(math.atan2(yeclip, xeclip)))
		#floatingpoint latt  =  math.atan2(zeclip, math.sqrt( xeclip*xeclip + yeclip*yeclip))
		#r =  math.sqrt(xeclip*xeclip + yeclip*yeclip + zeclip*zeclip)
	
		#Compensate for Moon's perturbations
		#Sun's  mean longitude:		Ls	 (already computed as Ls)
		#Moon's mean longitude:		Lm  =  N + w + Mm (for the Moon)
		#Sun's  mean anomaly:		  Ms	 (already computed as Ms)
		#Moon's mean anomaly:		  Mm	 (already computed in this function)
		#Moon's mean elongation:	   D   =  Lm - Ls
		#Moon's argument of latitude:  F   =  Lm - N
		
		Lm = N + w + Mm
		D  = Lm - Ls
		F = Lm - N
		#printf ("Moon's longt before perturb fix is %f\n", mlon)
		#printf ("Moon's uncorrected ecl. longitude = %.8f\n", mlon)
		
		#mlon in degrees
		mlon += -1.27388888 * math.sin(Mm - 2*D)	#Evection -- stjarnhimlen gives -1.274
		mlon += +0.65833333 * math.sin(2*D)			#Variation -- stjarnhimlen give +0.658
		mlon += -0.185 * math.sin(Ms)				#Yearly equation -- stjarnhimlen gives -0.186, but
													#[Chapront-Touzé and Chapront 1988] has 666 arc-seconds
		mlon += -0.059 * math.sin(2*Mm - 2*D)\
				-0.057 * math.sin(Mm - 2*D + Ms)\
				+0.053 * math.sin(Mm + 2*D)\
				+0.046 * math.sin(2*D - Ms)\
				+0.041 * math.sin(Mm - Ms)\
				-0.034722222 * math.sin(D)			#Parallactic equation [Chapront-Touzé and Chapront 1988] has
													#125 arc-seconds = 0.034722222
													#http://www.stjarnhimlen.se/comp/tutorial.html has 0.035
		mlon += -0.031 * math.sin(Mm + Ms)\
				-0.015 * math.sin(2*F - 2*D)		#reduction to the ecliptic from stjarnhimlen -- Wikipedia value is 0.0144
													#stjarnhimlen has 0.015
		mlon += +0.011 * math.sin(Mm - 4*D)
		#printf ("Moon's longt after perturb fix in radians is %f\n", mlon)
	
		#printf ("Sun's ecl. longitude = %.8f\n", slon)
		#printf ("Moon's ecl. longitude = %.8f\n", mlon)
		return mlon, slon

	def calculate_tithi_index(self, d, div):
		#Calculate Tithi and Paksha
		mlon, slon = self.calculate_moon_sun_long (d)
		fuzz = 0.03
		n = int(self.nround((self.rev(mlon-slon+fuzz)/div), 100000))
		#print ("Diff between Moons and Sun's longitudes =", mlon - slon)
		#print ("Index of diff between Moons and Sun's longitudes =", (mlon - slon)/12.0, " and index =", n)
		#print ("Tithi index is n=", n)
		return n

	def tithi (self, timescale):
		return self.calculate_tithi_index(timescale, 12.0) % 30

	def tithiday (self, dd, mm, yyyy, hr):
		timescale = self.ts_at_mn (dd, mm, yyyy) + (hr/24.0)
		t = self.tithi (timescale)
		#print ("tithi index t =", t)
		s = ("Shukla " if (t <= 14) else "Krishna ") + self.tithiList[t]
		print(s)
		return s

	def fpart (self, x):
		y = x - math.floor(x)
		if y < 0:
			y += 1
		return y

	def nround (self, x, n):
		#round up for +
		#round down for -
		#n is a power of 10
		if x == 0:
			return 0
		if x > 0:
			return math.floor(x*n + 0.5)/n
		else:
			return math.floor(x*n - 0.5)/n

	def sun (self, dd, mm, yyyy):
		#print ("sriseHr: ", sriseHr)
		timescale = self.ts_at_mn (dd, mm, yyyy) + 2451544 #2451543.5 + 12/24 (at noon)
		#Bangalore is 12.972N, 77.595E
		srise, sset, sunlightduration = self.sun_esrl (timescale,
							self.zoneHour, 
							self.latitude, 
							self.longitude)

		if (sunlightduration == 24.0):
			s = "No sunset on this day."
			srise = 24.0
			print (s)
		elif (sunlightduration == 0.0):
			s = "No sunrise on this day."
			srise = 0.0
			print (s)
		else:
			sriseh = int(srise)
			srisem = int(self.fpart(srise)*60)
			srises = int(self.nround(self.fpart(self.fpart(srise)*60)*60, 1000))

			sseth = int(sset)
			ssetm = int(self.fpart(sset)*60)
			ssets = int(self.nround(self.fpart(self.fpart(sset)*60)*60, 1000))

			dlh = int(sunlightduration)
			dlm = int(self.fpart(sunlightduration)*60)
			dls = int(self.nround(self.fpart(self.fpart(sunlightduration)*60)*60, 1000))

			s = f" Sunrise at: {sriseh:02}:{srisem:02}:{srises:02}\n" + \
				f" Sunset at : {sseth:02}:{ssetm:02}:{ssets:02}\n" + \
				f" Daylight hours: {dlh:02}:{dlm:02}:{dls:02}"
			print (s)

		return srise, s


/*
  Thanks for supporting Open-Hard/Soft-ware and thanks
  for all of the contributors to this project.

  For extra info on GRBL please have a look at my blog : 
	http://blog.protoneer.co.nz/tag/grbl/

  Grbl is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Grbl is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  http://www.gnu.org/licenses/
*/

/*
	Supported hardware:
		Arduino Duemilanove
		Arduino Uno
		Arduino Mega 2560 (Limited Testing)

*/
/*lista de comandos:
G0 para movimientos lineales
G1 X1 Y3 para mover cada eje, tambien esta el F3000 para mm/min, el Z0.5 mm para la alimentacion
G28 para calibrar
*/
#include <grblmain.h>

void setup(){
	startGrbl();
}

void loop(){}

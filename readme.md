## byond-tracy
byond-tracy glues together a byond server with the tracy profiler allowing you to analyze and visualize proc calls


## supported byond versions
| windows  | linux    |
| -------- | -------- |
| 516.1660 | 515.1660 |
| 516.1659 | 515.1659 |
| 516.1658 | 515.1658 |
| 516.1657 | 515.1657 |
| 516.1656 | 515.1656 |
| 516.1655 | 515.1655 |
| 516.1654 |   N/A    |
| 516.1653 | 515.1653 |
| 516.1652 | 515.1652 |
| 516.1651 | 515.1651 |
| 516.1650 | 515.1650 |
| 516.1649 | 515.1649 |
| 516.1648 | 515.1648 |
| 515.* | 515.* |
| 514.*| 515.* |

*except `515.1612` on Linux as there was no release*

## supported tracy versions
`0.8.1` `0.8.2` `0.9.0` `0.9.1` `0.10.0` `0.11.0` `0.11.1`

## usage
simply call `init` from `prof.dll` to begin collecting profile data and connect using [tracy-server](https://github.com/wolfpld/tracy/releases) `Tracy.exe`
```ts
/proc/prof_init()
	var/lib

	switch(world.system_type)
		if(MS_WINDOWS) lib = "prof.dll"
		if(UNIX) lib = "libprof.so"
		else CRASH("unsupported platform")

	var/init = call_ext(lib, "init")()
	if("0" != init) CRASH("[lib] init error: [init]")

/world/New()
	prof_init()
	. = ..()
```

## env vars
set these env vars before launching dreamdaemon to control which node and service to bind
```sh
UTRACY_BIND_ADDRESS
```

```sh
UTRACY_BIND_PORT
```

## building

You can download a precompiled byond-tracy executable from the [latest release](https://github.com/spacestation13/byond-tracy/releases/latest).

The Linux one is unlikely to work. No guarantee or warranty given for the binaries.

no build system included, simply invoke your preferred c11 compiler.
examples:
```sh
cl.exe /nologo /std:c11 /O2 /LD /DNDEBUG prof.c ws2_32.lib /Fe:prof.dll
```

```sh
clang.exe -std=c11 -m32 -shared -Ofast3 -DNDEBUG -fuse-ld=lld-link prof.c -lws2_32 -o prof.dll
```

```sh
gcc -std=c11 -m32 -shared -fPIC -Ofast -s -DNDEBUG prof.c -pthread -o libprof.so
```

## developing

To add offsets (required for every new BYOND version), you can derive them using https://github.com/Sovexe/byond-tracy-offset-extractor. 

Just run the `Extract Signatures` GitHub Workflow, and pass in your version like `["515.1590","515.1591"]`.

Ideally this just works perfectly. Go to the `Run extraction script` step and copy the offsets. It's already in copypaste form for the `byond_offsets` array in `prof.c`.

Then just PR it and maybe ping ZeWaka in #tooling-questions to merge it.

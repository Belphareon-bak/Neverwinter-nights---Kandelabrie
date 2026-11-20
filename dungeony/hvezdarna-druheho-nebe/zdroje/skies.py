"""Native sky models and painted panoramas for the two sides of the observatory."""

from math import cos, exp, pi, sin, tau
import random
import struct

from art import Material, Mesh


def cloud_octave(rng, width, height, columns, rows):
    """A smooth field that follows the sky's wrap-around longitude."""
    knots = [[rng.random() for _ in range(columns)] for _ in range(rows+1)]

    def weights(i, count, span):
        point = i*count/span
        cell = int(point)
        t = point-cell
        return cell, t*t*(3-2*t)

    xs = [weights(x,columns,width) for x in range(width)]
    ys = [weights(y,rows,height) for y in range(height)]

    def sample(x,y):
        i,u = xs[x]
        j,v = ys[y]
        next_i = (i+1)%columns
        a,b = knots[j],knots[j+1]
        return (a[i]*(1-u)+a[next_i]*u)*(1-v)+(b[i]*(1-u)+b[next_i]*u)*v

    return sample


def panorama(seed, upper, width=1024, height=512):
    """Paint a seamless longitude/elevation map with a cloud bank and a star band."""
    rng = random.Random(seed)
    stars = {}
    for i in range(2350 if upper else 1050):
        x, y = rng.randrange(width), rng.randrange(height//2 if upper else 119, height)
        hot = rng.randrange(43, 200)
        stars[x, y] = hot
        if i % 17 == 0:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                stars[(x + dx) % width, y + dy] = hot * .58

    angular = [tau * x / width for x in range(width)]
    ridge = [(.33 + .083 * sin(a + .31) + .041 * cos(2 * a - .33),
              .17 + .026 * sin(a * 3 + .37) + .022 * cos(a * 9)
              + .008 * sin(a * 19))
             for a in angular]
    if upper:
        vapor = [cloud_octave(rng,width,height,cols,rows)
                 for cols,rows in ((9,11),(23,31),(51,72))]
    pixels = bytearray()
    for y in range(height):
        v = y / (height - 1)
        horizon = exp(-((v - .215) * 6.2) ** 2)
        for x, theta in enumerate(angular):
            band, bank = ridge[x]
            folds = (.62 + .20 * sin(theta * 13 + sin(v * 37))
                     + .19 * sin(theta * 23 - v * 17))
            galaxy = exp(-((v - band) * 17.2) ** 2) * max(.05, folds) if upper else 0.0
            cloud = exp(-((v - bank) * 28.0) ** 2) * (.72 + .21 * sin(16 * theta + 17 * v)
                                                     + .11 * cos(31 * theta - 39 * v))
            light = stars.get((x, y), 0) * (1 - min(.91, cloud * .93))
            grain = (rng.random() - .5) * 3.5
            rgb = (11 + 17 * horizon + cloud * 91 + galaxy * 83 + light,
                   14 + 22 * horizon + cloud * 86 + galaxy * 61 + light,
                   30 + 36 * horizon + cloud * 100 + galaxy * 112 + light)
            if upper:
                haze = exp(-((v-.48)*7.4)**2)
                field = vapor[0](x,y)*.60 + vapor[1](x,y)*.30 + vapor[2](x,y)*.10
                front = (.96+.14*cos(theta*3+v*47)) * max(0,min(1,(.545-v)*21))
                bank = min(1.0,max(0.0,(field-.28)*1.8))**1.17
                cloud_light = front*(24+96*bank)
                fringe = exp(-((v-.495-.022*sin(theta*5)-.04*(field-.5))*30)**2)
                ribbon = .634 + .058*sin(theta+2.8) + .023*sin(theta*2+.7)
                veil = exp(-((v-ribbon)*25)**2)*(.42+.73*field)
                rgb = (10 + 12*haze + cloud_light*.91 + fringe*28 + veil*50 + light*.83,
                       16 + 15*haze + cloud_light + fringe*31 + veil*76 + light*.84,
                       34 + 20*haze + cloud_light*1.16 + fringe*46 + veil*107 + light*.95)
            pixels.extend(max(0, min(255, int(channel + grain))) for channel in reversed(rgb))
    header = struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, width, height, 24, 0)
    return header + pixels


def sky_model(name, bitmap, upper):
    mesh = Mesh()
    material = Material((1, 1, 1), bitmap, (1, 1, 1))
    columns, rows, radius = 56, 36, 195.0
    low, high = (-pi/2 + .01 if upper else -pi/6), pi/2
    def point(u, v):
        azimuth = u * tau
        elevation = low + (high - low) * v
        return (radius * cos(elevation) * cos(azimuth),
                radius * cos(elevation) * sin(azimuth),
                radius * sin(elevation))
    for j in range(rows):
        for i in range(columns):
            a, b, c, d = i / columns, (i + 1) / columns, j / rows, (j + 1) / rows
            uv = ((a, c), (a, d), (b, d), (b, c))
            mesh.polygon(material, [point(*pair) for pair in uv], uv)
    return mesh.mdl(name).replace(b"classification Other", b"classification Effect")


def sky_assets(game):
    base = game.read("skyboxes", "2da").rstrip()
    first = int(base.splitlines()[-1].split()[0]) + 1
    descriptions, resources, rows = {}, {}, []
    for index, (key, label) in enumerate((("rim", "Hvezdarna_Hory"), ("upper", "Hvezdarna_DruheNebe"))):
        ident = first + index
        model, bitmap = f"hvd_sky_{key}", f"hvd_pan_{key}"
        descriptions[key] = ident
        rows.append(f"{ident} {label} **** 0 {model} {model} {model} {model}")
        resources[f"{model}.mdl"] = sky_model(model, bitmap, key == "upper")
        resources[f"{bitmap}.tga"] = panorama(734 + index * 23, key == "upper")
    resources["skyboxes.2da"] = base + b"\r\n" + "\r\n".join(rows).encode("ascii") + b"\r\n"
    return descriptions, resources

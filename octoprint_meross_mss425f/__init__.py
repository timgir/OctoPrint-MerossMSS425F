import asyncio
import octoprint.plugin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager


async def shutdown(email, password, id_plugs):
	http_api_client = await MerossHttpClient.async_from_user_password(email=email,
																	  password=password)

	manager = MerossManager(http_client=http_api_client)
	await manager.async_init()

	await manager.async_device_discovery()
	plugs = manager.find_devices(device_type='mss310') or manager.find_devices(device_type='mss425e') or manager.find_devices(device_type='mss425f')

	if len(plugs) > 0:
		plug = plugs[0]

		# Single plug capability
		if plug.type == 'mss310':
			await plug.async_update()
			await asyncio.sleep(1)
			await plug.async_turn_off(channel=0)
			await asyncio.sleep(1)
		else:
			for id_plug in id_plugs:
				await plug.async_update()
				await asyncio.sleep(1)
				await plug.async_turn_off(channel=id_plug)
				await asyncio.sleep(1)

	manager.close()
	await http_api_client.async_logout()


class MerossMss425fPlugin(octoprint.plugin.AssetPlugin,
						  octoprint.plugin.SettingsPlugin,
						  octoprint.plugin.StartupPlugin,
						  octoprint.plugin.TemplatePlugin):

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			email='',
			password='',
			multiplug = dict(
				first_plug=False,
				second_plug=False,
				third_plug=False,
				fourth_plug=False,
				usb_plug=False
			)
		)

	def get_template_configs(self):
		return [
			dict(type='settings', custom_bindings=False)
		]

	##~~ AssetPlugin mixin

	def get_assets(self):
		return dict(
			less=["less/meross-mss425f.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			meross_mss425f=dict(
				displayName="Octoprint-merossmss425f Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="timgir",
				repo="OctoPrint-MerossMSS425F",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/timgir/OctoPrint-MerossMSS425F/archive/{target_version}.zip"
			)
		)

	def hook_gcode_queuning(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		if gcode == 'M81':
			email = self._settings.get(['email'])
			password = self._settings.get(['password'])
			multiplug = self._settings.get(['multiplug'])

			id_plug = []

			if 'first_plug' in multiplug and multiplug['first_plug'] is True:
				id_plug.append(1)
			if 'second_plug' in multiplug and multiplug['second_plug'] is True:
				id_plug.append(2)
			if 'third_plug' in multiplug and multiplug['third_plug'] is True:
				id_plug.append(3)
			if 'fourth_plug' in multiplug and multiplug['fourth_plug'] is True:
				id_plug.append(4)
			if 'usb_plug' in multiplug and multiplug['usb_plug'] is True:
				id_plug.append(5)

			if email != '' and password != '':
				try:
					asyncio.run(shutdown(email, password, id_plug))
				except RuntimeError:
					loop = asyncio.get_running_loop()
					loop.run_until_complete(shutdown(email, password, id_plug))
			else:
				self._logger.info('Connection information are not been set !')


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Meross MSS425F"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = MerossMss425fPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.hook_gcode_queuning,
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

